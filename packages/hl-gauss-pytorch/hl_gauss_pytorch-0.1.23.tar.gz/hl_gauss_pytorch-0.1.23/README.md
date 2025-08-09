<img src="./fig2.png" width="500px"></img>

## HL Gauss - Pytorch

The Gaussian Histogram Loss (HL-Gauss) proposed by [Imani et al.](https://proceedings.mlr.press/v80/imani18a/imani18a.pdf) with a few convenient wrappers, in Pytorch.

A team at Deepmind wrote a [paper](https://arxiv.org/abs/2403.03950) with a lot of positive findings for its use in value-based RL.

Put into action [here](https://github.com/lucidrains/phasic-policy-gradient), seems to work well

## Install

```bash
$ pip install hl-gauss-pytorch
```

## Usage

The `HLGaussLoss` module as defined in Appendix A. of the [Stop Regressing paper](https://arxiv.org/abs/2403.03950)

```python
import torch
from hl_gauss_pytorch import HLGaussLoss

hl_gauss = HLGaussLoss(
    min_value = 0.,
    max_value = 5.,
    num_bins = 32,
    sigma = 0.5,
    clamp_to_range = True # this was added because if any values fall outside of the bins, the loss is 0 with the current logic
)

logits = torch.randn(3, 16, 32).requires_grad_()
targets = torch.randint(0, 5, (3, 16)).float()

loss = hl_gauss(logits, targets)
loss.backward()

# after much training

pred_target = hl_gauss(logits) # (3, 16)
```

For a convenient layer that predicts from embedding to logits, import `HLGaussLayer`

```python
import torch
from hl_gauss_pytorch import HLGaussLayer

hl_gauss_layer = HLGaussLayer(
    dim = 256, # input embedding dimension
    hl_gauss_loss = dict(
        min_value = 0.,
        max_value = 5.,
        num_bins = 32,
        sigma = 0.5,
    )
)

embed = torch.randn(7, 256)
targets = torch.randint(0, 5, (7,)).float()

loss = hl_gauss_layer(embed, targets)
loss.backward()

# after much training

pred_target = hl_gauss_layer(embed) # (7,)
```

For ablating the proposal, you can make the `HLGaussLayer` fall back to regular regression by setting `use_regression = True`, keeping the code above unchanged

```python
HLGaussLayer(..., use_regression = True)
```

## Citations

```bibtex
@article{Imani2024InvestigatingTH,
    title   = {Investigating the Histogram Loss in Regression},
    author  = {Ehsan Imani and Kai Luedemann and Sam Scholnick-Hughes and Esraa Elelimy and Martha White},
    journal = {ArXiv},
    year    = {2024},
    volume  = {abs/2402.13425},
    url     = {https://api.semanticscholar.org/CorpusID:267770096}
}
```

```bibtex
@inproceedings{Imani2018ImprovingRP,
    title   = {Improving Regression Performance with Distributional Losses},
    author  = {Ehsan Imani and Martha White},
    booktitle = {International Conference on Machine Learning},
    year    = {2018},
    url     = {https://api.semanticscholar.org/CorpusID:48365278}
}
```

```bibtex
@article{Farebrother2024StopRT,
    title   = {Stop Regressing: Training Value Functions via Classification for Scalable Deep RL},
    author  = {Jesse Farebrother and Jordi Orbay and Quan Ho Vuong and Adrien Ali Taiga and Yevgen Chebotar and Ted Xiao and Alex Irpan and Sergey Levine and Pablo Samuel Castro and Aleksandra Faust and Aviral Kumar and Rishabh Agarwal},
    journal = {ArXiv},
    year   = {2024},
    volume = {abs/2403.03950},
    url    = {https://api.semanticscholar.org/CorpusID:268253088}
}
```
