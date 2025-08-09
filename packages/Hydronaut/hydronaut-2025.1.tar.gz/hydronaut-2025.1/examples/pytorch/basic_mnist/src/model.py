#!/usr/bin/env python3

'''
Adaptation of the PyTorch Basic MNIST Example:
https://github.com/pytorch/examples/blob/main/mnist/main.py
'''
import logging

import torch
from torch import nn
import torch.nn.functional as F
from torch import optim
from torch.optim.lr_scheduler import StepLR
from torchvision import datasets, transforms

# tqdm is only required for printing progress bars on the terminal
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm


# Use a standard logger to replace the print statements for homogeneous output.
# Even without Hydronaut it is recommended to use standard logging functions.
LOGGER = logging.getLogger(__name__)


class Net(nn.Module):  # pylint: disable=too-few-public-methods
    '''
    Example nn.Module subclass.
    '''
    def __init__(self, params):
        super().__init__()

        # Get the model parameters from the configuration object.
        self.params = params
        conv1 = params.conv1
        conv2 = params.conv2

        # Calculate the input size to the fully connected layer based on the current
        # parameters.
        #
        # Each convolution layer reduces each image dimension by ( [(D - K) / S] + 1) where
        # D is the input dimension (width or height), K is the kernel size, [] represents the
        # floor function, and S is the stride.
        #
        # The pooling layer applied below in forward() also reduces the dimension by [D / P]
        # where P is the value passed to max_pool2d.
        #
        # The resulting flattened size is D * D * CO_2 where CO_2 is the number of output
        # channels from the second convolution layer.
        input_dim = 28  # fixed MNIST input dimension
        after_conv1_dim = ((input_dim - conv1.kernel_size) // conv1.stride) + 1
        after_conv2_dim = ((after_conv1_dim - conv2.kernel_size) // conv2.stride) + 1
        after_pool_dim = after_conv2_dim // params.max_pool2d
        fc_size = after_pool_dim * after_pool_dim * conv2.out_channels

        # The updated code.
        self.conv1 = nn.Conv2d(1, conv1.out_channels, conv1.kernel_size, conv1.stride)
        self.conv2 = nn.Conv2d(
            conv1.out_channels,
            conv2.out_channels,
            conv2.kernel_size,
            conv2.stride
        )
        self.dropout1 = nn.Dropout(params.dropout1)
        self.dropout2 = nn.Dropout(params.dropout2)
        self.fc1 = nn.Linear(fc_size, params.fc1)
        self.fc2 = nn.Linear(params.fc1, 10)

    def forward(self, x):  # pylint: disable=invalid-name
        '''
        Forward method.
        '''
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, self.params.max_pool2d)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)  # pylint: disable=no-member
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output


def train(  # pylint: disable=too-many-arguments
    params,
    model,
    device,
    train_loader,
    optimizer,
    epoch
):
    '''
    Train the model.

    Args:
        params:
            Training parameters.

        model:
            The model.

        device:
            The PyTorch device on which to train the model.

        train_loader:
            The DataLoader for the training data.

        optimizer:
            The training optimizer.

        epoch:
            The epoch number.
    '''
    model.train()
    with logging_redirect_tqdm():
        for batch_idx, (data, target) in enumerate(tqdm(train_loader)):
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = F.nll_loss(output, target)
            loss.backward()
            optimizer.step()
            if batch_idx % params.log_interval == 0:
                # Transform a print statement to a logging function.
                LOGGER.info(
                    'Train Epoch: %s [%d/%d (%.0f%%)]\tLoss: %0.6f',
                    epoch, batch_idx * len(data), len(train_loader.dataset),
                    100. * batch_idx / len(train_loader), loss.item()
                )
                if params.dry_run:
                    break


def test(model, device, test_loader):
    '''
    Test the trained model.

    Args:
        model:
            The trained model.

        device:
            the PyTorch device on which to test the model.

        test_loader:
            The Dataloader for the test data.

    Returns:
        The test loss and accuracy.
    '''
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)
    accuracy = correct / len(test_loader.dataset)

    # Transform a print statement to a logging function.
    LOGGER.info(
        'Test set: Average loss: %0.4f, Accuracy %d/%d (%.0f%%)',
        test_loss, correct, len(test_loader.dataset),
        100. * accuracy
    )

    # Return some metrics for optimization.
    return test_loss, accuracy


def main(config):  # pylint: disable=too-many-locals
    '''
    Load the data then train and test the model.

    Returns:
        The trained model, the average loss and the test accuracy.
    '''
    params = config.experiment.params
    meta_params = params.meta
    training_params = params.training

    use_cuda = not meta_params.no_cuda and torch.cuda.is_available()
    use_mps = not meta_params.no_mps and torch.backends.mps.is_available()

    torch.manual_seed(meta_params.seed)

    if use_cuda:
        device = torch.device("cuda")  # pylint: disable=no-member
    elif use_mps:
        device = torch.device("mps")  # pylint: disable=no-member
    else:
        device = torch.device("cpu")  # pylint: disable=no-member
    LOGGER.info('Device: %s', device)

    train_kwargs = {'batch_size': training_params.batch_size}
    test_kwargs = {'batch_size': training_params.test_batch_size}
    if use_cuda:
        cuda_kwargs = {
            'num_workers': 1,
            'pin_memory': True,
            'shuffle': True
        }
        train_kwargs.update(cuda_kwargs)
        test_kwargs.update(cuda_kwargs)

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    data_dir = params.data_dir
    dataset1 = datasets.MNIST(data_dir, train=True, download=True, transform=transform)
    dataset2 = datasets.MNIST(data_dir, train=False, transform=transform)
    train_loader = torch.utils.data.DataLoader(dataset1, **train_kwargs)
    test_loader = torch.utils.data.DataLoader(dataset2, **test_kwargs)

    model = Net(params.model).to(device)
    optimizer = optim.Adadelta(model.parameters(), lr=training_params.lr)

    scheduler = StepLR(optimizer, step_size=1, gamma=training_params.gamma)
    # Get the metrics
    avg_loss = None
    accuracy = None
    for epoch in range(1, training_params.epochs + 1):
        train(meta_params, model, device, train_loader, optimizer, epoch)
        avg_loss, accuracy = test(model, device, test_loader)
        scheduler.step()

    # Return the model and the metrics.
    return model, avg_loss, accuracy
