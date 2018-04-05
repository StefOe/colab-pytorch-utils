# colab-tf-utils
Simple GDrive-Based file saving from within Google's Colab service


Usage Example:

    !wget https://raw.githubusercontent.com/StefOe/colab-tf-utils/master/utils.py
    import utils
    from torchvision.models import AlexNet

    m = AlexNet()
    gsync = GDriveSync()
    torch.save("model.pt")
    gsync.upload_file_to_folder("model.pt")
