import torch
import torch.nn as nn


def emd(template: torch.Tensor, source: torch.Tensor):
    emd_loss = torch.mean(self.emd(template, source)) / (template.size()[1])
    return emd_loss


class EMDLoss(nn.Module):
    def __init__(self):
        super(EMDLoss, self).__init__()

    def forward(self, template, source):
        return emd(template, source)
