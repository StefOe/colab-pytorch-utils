# colab-pytorch-utils
Simple GDrive-Based file saving from within Google's Colab service


Usage Example:

    !wget https://raw.githubusercontent.com/StefOe/colab-pytorch-utils/master/utils.py
    import utils
    from torchvision.models import AlexNet

    m = AlexNet()
    gsync = utils.GDriveSync()
    torch.save("model.pt")
    gsync.update_file_to_folder("model.pt")

Careful, at the moment all files with the same filename will be deleted from your GDrive.
