# Learning to Compare: Relation Network for Few-Shot Learning using Pytorch

A implementation of the CVPR 2018 paper : [Learning to Compare: Relation Network for Few-Shot Learning](https://arxiv.org/pdf/1711.06025.pdf) using pytorch. In the model, somethings, such as learning rates or regression, may differ from the original paper.

I will post the details of the code in ***Korean*** on my [blog]()(will be soon.) so if you are interested, please visit!

한글로 논문과 코드에 대해 작성한 글이 있으니 관심있으신 분은 확인해보세요!

### 🚀How to run

1. #### Go into prototypical directory

   ```bash
   cd relation
   ```

2. #### Train

   This commend will train the model.

   ```bash
   python train.py
   ```

3. #### Test

   If trained models are exists, you can test the model. Below command will test the entire model in `runs/exp_name` 

   ```bash
   python eval.py
   ```
   
4. #### Logs

   Train logs, saved model and configuration data were in `run/exp_name`. Logs are made by `tensorboard`. So if you want to see more detail about train metrics, write commend on like this.

   ```bash
   tensorboard --logdir=runs
   ```

   

All parameters are present in `arguments.py`. If you want to adjust the parameters, modify them and run the code.

### 📈Result

| Model                | Reference Paper | This Repo |
| -------------------- | --------------- | --------- |
| Omniglot 5-w 1-s     | 99.6±0.2%       | 99.6%     |
| Omniglot 5-w 5-s     | 99.8±0.1%       | 99.7%     |
| Omniglot 20-w 1-s    | 97.6±0.2%       | 97.3%     |
| Omniglot 20-w 1-s    | 99.1±0.1        | 99.1%     |
| miniImageNet 5-w 1-s | 50.44±0.82%     | 51.2±0.3% |
| miniImageNet 5-w 5-s | 65.32±0.66%     | 65.6±0.2% |

![omniglot_result](asset/omniglot_result.png)

### 📌Reference

* [Learning to Compare: Relation Network for Few-Shot Learning](https://arxiv.org/pdf/1711.06025.pdf)
* [floodsung/LearningToCompare_FSL](https://github.com/floodsung/LearningToCompare_FSL)

