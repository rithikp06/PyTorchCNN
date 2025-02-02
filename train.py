import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torchvision
import torchvision.transforms as transforms
import torchvision.datasets as datasets
from Model import CNN
from Dataset import MNISTDistilled
from tqdm import tqdm


device = ("cuda" if torch.cuda.is_available() else "cpu")

transform = transforms.Compose(
        [
            transforms.Resize((356, 356)),
            transforms.Grayscale(3),
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,)),
        ]
    )

mnist = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)

mnist_testset = mnist
num_epochs = 10
learning_rate = 0.00001
train_CNN = False
batch_size = 10
shuffle = True
pin_memory = True
num_workers = 0

dataset = MNISTDistilled("distilled", "train_csv.csv",transform=transform)
# train_set, validation_set = torch.utils.data.random_split(dataset,[20000,5000])
train_set = torch.load('tensor_step000_all.pt')
print(train_set.shape)
# train_set = torch.from_numpy(train_set)
validation_set = mnist_testset
# train_set = mnist_testset
# validation_set = dataset
mnist_loader = torch.utils.data.DataLoader(dataset=mnist,
                                               batch_size=batch_size,
                                               shuffle=True,
                                               num_workers=num_workers)

# train_loader = DataLoader(dataset=train_set, shuffle=shuffle, batch_size=batch_size,num_workers=num_workers,pin_memory=pin_memory)
# validation_loader = DataLoader(dataset=validation_set, shuffle=shuffle, batch_size=batch_size,num_workers=num_workers, pin_memory=pin_memory)
train_loader = mnist_loader
validation_loader =  mnist_loader
model = CNN().to(device)

criterion = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

for name, param in model.inception.named_parameters():
    if "fc.weight" in name or "fc.bias" in name:
        param.requires_grad = True
    else:
        param.requires_grad = train_CNN

def check_accuracy(loader, model):
    if loader == train_loader:
        print("Checking accuracy on training data")
    else:
        print("Checking accuracy on validation data")

    num_correct = 0
    num_samples = 0
    model.eval()

    with torch.no_grad():
        print("Checking accuracy 2")
        for x, y in loader:
            print("Checking accuracy")
            x = x.to(device=device)
            y = y.to(device=device)
            print("Checking accuracy 4")
            scores = model(x)
            print("Checking accuracy 5")
            predictions = torch.tensor([1.0 if i >= 0.5 else 0.0 for i in scores]).to(device)
            print("Checking accuracy 6")
            num_correct += (predictions == y).sum()
            num_samples += predictions.size(0)
            print("Checking accuracy 7")
    return f"{float(num_correct)/float(num_samples)*100:.2f}"
    print(
        f"Got {num_correct} / {num_samples} with accuracy {float(num_correct)/float(num_samples)*100:.2f}"
    )
    model.train()

def train():
    model.train()
    for epoch in range(num_epochs):
        loop = tqdm(train_loader, total = len(train_loader), leave = True)
        if epoch % 2 == 0:
            loop.set_postfix(val_acc = check_accuracy(validation_loader, model))
        for imgs, labels in loop:
            imgs = imgs.to(device)
            labels = labels.to(device)
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            loop.set_description(f"Epoch [{epoch}/{num_epochs}]")
            loop.set_postfix(loss = loss.item())

if __name__ == "__main__":
    train()