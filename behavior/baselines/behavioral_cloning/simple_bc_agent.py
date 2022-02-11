"""
Behavioral cloning agent network architecture and training
"""
import argparse
import logging
import sys

sys.path.insert(0, "../utils")
import base_input_utils as BIU
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

log = logging.getLogger(__name__)


class BCNet_rgbp(nn.Module):
    """A behavioral cloning agent that uses RGB images and proprioception as state space"""

    def __init__(self, img_channels=3, proprioception_dim=20, num_actions=28):
        super(BCNet_rgbp, self).__init__()
        # image feature
        self.features1 = nn.Sequential(
            nn.Conv2d(img_channels, 32, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1),
            nn.ReLU(),
        )
        self.flatten = nn.Flatten()
        self.features2 = nn.Sequential(nn.Linear(proprioception_dim, 40), nn.ReLU())
        self.fc4 = nn.Linear(9216 + 40, 512)
        self.fc5 = nn.Linear(512, num_actions)

    def forward(self, imgs, proprioceptions):
        x1 = self.features1(imgs)
        x1 = self.flatten(x1)
        x2 = self.features2(proprioceptions)
        x = torch.cat((x1, x2), dim=1)
        x = self.fc4(x)
        x = F.relu(x)
        x = self.fc5(x)
        return x


class BCNet_taskObs(nn.Module):
    def __init__(self, task_obs_dim=456, proprioception_dim=20, num_actions=28):
        super(BCNet_taskObs, self).__init__()
        # image feature
        self.fc1 = nn.Linear(task_obs_dim + proprioception_dim, 1024)
        self.fc2 = nn.Linear(1024, 256)
        self.fc3 = nn.Linear(256, num_actions)

    def forward(self, task_obs, proprioceptions):
        x = torch.cat((task_obs, proprioceptions), dim=1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        x = F.relu(x)
        x = self.fc3(x)
        return x


if __name__ == "__main__":

    def parse_args():
        parser = argparse.ArgumentParser(description="Dataset loader")
        parser.add_argument("--spec", type=str, help="spec file name")
        return parser.parse_args()

    args = parse_args()
    data = BIU.BHDataset(args.spec)
    data.to_device()

    # Training
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # bc_agent = BCNet_rgbp().to(device)
    bc_agent = BCNet_taskObs().to(device)
    optimizer = optim.Adam(bc_agent.parameters())

    NUM_EPOCH = 5
    PATH = "trained_models/model.pth"

    for epoch in range(NUM_EPOCH):
        optimizer.zero_grad()
        output = bc_agent(data.task_obss, data.proprioceptions)
        loss_func = nn.MSELoss()
        loss = loss_func(output, data.actions)
        loss.backward()
        optimizer.step()

        log.info(loss.item())

    torch.save(bc_agent, PATH)
