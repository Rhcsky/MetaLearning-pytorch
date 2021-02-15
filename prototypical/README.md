# Prototypical Networks for Few Shot Learning using Pytorch
A implementation of the NIPS 2017 paper : [Prototypical Networks for Few Shot Learning](https://arxiv.org/pdf/1703.05175.pdf) using pytorch. In the model, somethings, such as learning rates or regression, may differ from the original paper.

I posted the details of the code in ***Korean*** on my [blog](https://rhcsky.tistory.com/10), so if you are interested, please visit!

한글로 논문과 코드에 대해 작성한 글이 있으니 관심있으신 분은 확인해보세요!

### 🚀How to run

1. #### Go into prototypical directory

   ```bash
   cd prototypical
   ```

2. #### Train

   This commend will train the model. You can set the model and dataset option. Model's default is `protonet` and you can also set `resnet`. Dataset's default is `omniglot` and also you can choose `miniImagenet`

   ```bash
   python train.py -d omniglot -m protonet
   ```

3. #### Test

   If trained models are exists, you can test the model. Below command will test the entire model in `runs/exp_name` 

   ```bash
   python test.py
   ```

All parameters are present in `arguments.py`. If you want to adjust the parameters, modify them and run the code.

### 📈Result

Train logs, saved model and configuration data were in `run/exp_name`. Logs are made by `tensorboard`. So if you want to see more detail about train metrics, write commend on like this.

```
tensorboard --logdir=runs
```





### 📌Reference

* [Prototypical Networks for Few Shot Learning](https://arxiv.org/pdf/1703.05175.pdf)

* [orobix/Prototypical-Networks-for-Few-shot-Learning-PyTorch](https://github.com/orobix/Prototypical-Networks-for-Few-shot-Learning-PyTorch)

