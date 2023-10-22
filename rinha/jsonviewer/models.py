from django.db import models


class JSONData(models.Model):
    json_file = models.FileField(upload_to='json_files/')
