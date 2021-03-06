import os
import sys
from glob import glob

sys.path.append(os.path.dirname(os.path.realpath(os.path.dirname(__file__))))

import torch
import torch.backends.cudnn as cudnn
from torch.utils.tensorboard import SummaryWriter
import numpy as np

from arguments import get_args
from dataloader import get_dataloader
from relationnet import RelationNetwork, Embedding
from utils.train_utils import AverageMeter, save_checkpoint, plot_classes_preds
from utils.common import split_support_query_set

best_acc1 = 0
device = 'cuda' if torch.cuda.is_available() else 'cpu'
args = get_args()
writer = SummaryWriter(args.log_dir)


def main():
    global args, best_acc1, device

    # Init seed
    np.random.seed(args.manual_seed)
    torch.manual_seed(args.manual_seed)
    torch.cuda.manual_seed(args.manual_seed)

    if args.dataset == 'miniImageNet':
        train_loader, val_loader = get_dataloader(args, 'train', 'val')
        in_channel = 3
        feature_dim = 64 * 3 * 3
    elif args.dataset == 'omniglot':
        train_loader, val_loader = get_dataloader(args, 'trainval', 'test')
        in_channel = 1
        feature_dim = 64
    else:
        raise ValueError(f"Dataset {args.dataset} is not supported")

    embedding = Embedding(in_channel).to(device)
    model = RelationNetwork(feature_dim).to(device)

    criterion = torch.nn.MSELoss()

    embed_optimizer = torch.optim.Adam(embedding.parameters(), args.lr)
    model_optimizer = torch.optim.Adam(model.parameters(), args.lr)

    cudnn.benchmark = True

    if args.resume:
        try:
            checkpoint = torch.load(sorted(glob(f'{args.log_dir}/checkpoint_*.pth'), key=len)[-1])
        except Exception:
            checkpoint = torch.load(args.log_dir + '/model_best.pth')
        model.load_state_dict(checkpoint['model_state_dict'])
        embedding.load_state_dict(checkpoint['embedding_state_dict'])
        model_optimizer.load_state_dict(checkpoint['model_optimizer_state_dict'])
        embed_optimizer.load_state_dict(checkpoint['embed_optimizer_state_dict'])
        start_epoch = checkpoint['epoch']
        best_acc1 = checkpoint['best_acc1']

        print(f"load checkpoint {args.exp_name}")
    else:
        start_epoch = 1

    embed_scheduler = torch.optim.lr_scheduler.MultiplicativeLR(optimizer=embed_optimizer,
                                                                lr_lambda=lambda epoch: 0.5)
    model_scheduler = torch.optim.lr_scheduler.MultiplicativeLR(optimizer=model_optimizer,
                                                                lr_lambda=lambda epoch: 0.5)

    for _ in range(start_epoch):
        embed_scheduler.step()
        model_scheduler.step()

    print(f"model parameter : {sum(p.numel() for p in model.parameters() if p.requires_grad)}")

    for epoch in range(start_epoch, args.epochs + 1):

        train_loss = train(train_loader, model, embedding, model_optimizer, embed_optimizer, criterion, epoch)

        is_test = False if epoch % args.test_iter else True
        if is_test or epoch == args.epochs or epoch == 1:

            val_loss, acc1 = validate(val_loader, model, embedding, criterion, epoch)

            if acc1 >= best_acc1:
                is_best = True
                best_acc1 = acc1
            else:
                is_best = False

            save_checkpoint({
                'model_state_dict': model.state_dict(),
                'embedding_state_dict': embedding.state_dict(),
                'model_optimizer_state_dict': model_optimizer.state_dict(),
                'embed_optimizer_state_dict': embed_optimizer.state_dict(),
                'best_acc1': best_acc1,
                'epoch': epoch,
            }, is_best, args)

            if is_best:
                writer.add_scalar("BestAcc", acc1, epoch)

            print(f"[{epoch}/{args.epochs}] {train_loss:.3f}, {val_loss:.3f}, {acc1:.3f}, # {best_acc1:.3f}")

        else:
            print(f"[{epoch}/{args.epochs}] {train_loss:.3f}")

        embed_scheduler.step()
        model_scheduler.step()

    writer.close()


def train(train_loader, model, embedding, model_optimizer, embed_optimizer, criterion, epoch):
    losses = AverageMeter()
    num_class = args.classes_per_it_tr
    num_support = args.num_support_tr
    num_query = args.num_query_tr
    total_epoch = len(train_loader) * (epoch - 1)

    model.train()
    embedding.train()
    for i, data in enumerate(train_loader):
        x, y = data[0].to(device), data[1].to(device)
        x_support, x_query, y_support, y_query = split_support_query_set(x, y, num_class, num_support, num_query)

        support_vector = embedding(x_support)
        query_vector = embedding(x_query)

        _size = support_vector.size()

        support_vector = support_vector.view(num_class, num_support, _size[1], _size[2], _size[3]).sum(dim=1)
        support_vector = support_vector.repeat(num_class * num_query, 1, 1, 1)
        query_vector = torch.stack([x for x in query_vector for _ in range(num_class)])

        _concat = torch.cat((support_vector, query_vector), dim=1)

        y_pred = model(_concat).view(-1, num_class)

        y_one_hot = torch.zeros(num_query * num_class, num_class).to(device).scatter_(1, y_query.unsqueeze(1), 1)
        loss = criterion(y_pred, y_one_hot)

        losses.update(loss.item(), y_pred.size(0))

        model_optimizer.zero_grad()
        embed_optimizer.zero_grad()
        loss.backward()
        model_optimizer.step()
        embed_optimizer.step()

        if i == 0:
            y_hat = y_pred.argmax(1)
            writer.add_figure('y_prediction vs. y/Train',
                              plot_classes_preds(y_hat, y_pred, [x_support, x_query],
                                                 [y_support, y_query], num_class, num_support, num_query),
                              global_step=total_epoch)
        writer.add_scalar("Loss/Train", loss.item(), total_epoch + i)

    return losses.avg


@torch.no_grad()
def validate(val_loader, model, embedding, criterion, epoch):
    losses = AverageMeter()
    accuracies = AverageMeter()

    num_class = args.classes_per_it_val
    num_support = args.num_support_val
    num_query = args.num_query_val
    total_epoch = len(val_loader) * (epoch - 1)

    model.eval()
    embedding.eval()
    for i, data in enumerate(val_loader):
        x, y = data[0].to(device), data[1].to(device)
        x_support, x_query, y_support, y_query = split_support_query_set(x, y, num_class, num_support, num_query)

        support_vector = embedding(x_support)
        query_vector = embedding(x_query)

        _size = support_vector.size()

        support_vector = support_vector.view(num_class, num_support, _size[1], _size[2], _size[3]).sum(dim=1)
        support_vector = support_vector.repeat(num_class * num_query, 1, 1, 1)
        query_vector = torch.stack([x for x in query_vector for _ in range(num_class)])

        _concat = torch.cat((support_vector, query_vector), dim=1)

        y_pred = model(_concat).view(-1, num_class)

        y_one_hot = torch.zeros(num_query * num_class, num_class).to(device).scatter_(1, y_query.unsqueeze(1), 1)
        loss = criterion(y_pred, y_one_hot)

        losses.update(loss.item(), y_pred.size(0))

        y_hat = y_pred.argmax(1)
        accuracy = y_hat.eq(y_query).float().mean()
        accuracies.update(accuracy)

        if i == 0:
            y_hat = y_pred.argmax(1)
            writer.add_figure('y_prediction vs. y/Val',
                              plot_classes_preds(y_hat, y_pred, [x_support, x_query],
                                                 [y_support, y_query], num_class, num_support, num_query),
                              global_step=total_epoch)
        writer.add_scalar("Loss/Val", loss.item(), total_epoch + i)
        writer.add_scalar("Acc/Val", accuracy, total_epoch + i)

    return losses.avg, accuracies.avg


if __name__ == '__main__':
    main()
