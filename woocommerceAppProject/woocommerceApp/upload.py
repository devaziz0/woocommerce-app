import os

def upload_to_profile_photo(instance, filename):
    root = 'profiles/photos/'
    extension = os.path.splitext(filename)[-1]
    filename = 'profile_pic'
    return root + filename + extension

def upload_to_workshop_cover(instance, filename):
    root = 'workshop/covers/'
    extension = os.path.splitext(filename)[-1]
    filename = instance.title + '_' + str(int(instance.start_date.timestamp()))
    return root + filename + extension

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    root = 'profiles/'+instance.profil.user.username+ str(instance.profil.user.id)+'/'
    extension = os.path.splitext(filename)[-1]
    filename = 'schedule' + '_' + str(instance.id)
    return root + filename + extension
