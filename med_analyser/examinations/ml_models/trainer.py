from datetime import datetime
import pandas as pd
import shutil, os
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from fastai.vision.transform import get_transforms
from fastai.vision.data import imagenet_stats
from fastai.vision import *
from django.conf import settings


def train_chest_xray_model(learners_findings, confirmed_findings_model, image_type_model, examinations_model):
    path = Path(os.path.join(settings.MEDIA_ROOT))
    images_path = path/'examination_images'
    
    # iterate over all image types
    for image_type in image_type_model.objects.all():

        # get confirmed findings querysets for current image type
        qs_cfs_for_image_type = confirmed_findings_model.objects.filter(marked_for_training=False, training_complete=False, examination__image_type=image_type)
        if not qs_cfs_for_image_type: continue

        qs_cfs_for_image_type.update(marked_for_training=False)
        qs_cfs_for_image_type.update(training_complete=True)
        examinations_in_qs_cfs_for_image_type = examinations_model.objects.filter(confirmedfinding__in=qs_cfs_for_image_type)

        image_list = []
        tags_list = []
        for examination in examinations_in_qs_cfs_for_image_type:
            qs_cfs_for_examination = qs_cfs_for_image_type.filter(examination=examination)
            confirmed_findings = [cf.finding.label for cf in qs_cfs_for_examination]
            tags_list.append(';'.join(confirmed_findings))

            image = str(examination.image.path).partition("/web/media/examination_images/")[2]
            image_list.append(image)
            
        df = pd.DataFrame({'name': image_list, 'tags': tags_list})
 
        tfms = get_transforms(flip_vert=False, max_warp=0.) 
        data = (ImageList.from_df(df=df, path=images_path)
                .split_by_rand_pct(0.2)
                .label_from_df(label_delim=';')
                .transform(tfms, size=224)
                .databunch(bs=8).normalize(imagenet_stats))
        
        try: 
            learn = learners_findings[image_type.label]
            learn.unfreeze()
            learn.fit_one_cycle(1, slice(1e-5, 1e-3))
            learn.save(str(datetime.datetime.now()))
            print('saved learner')
        except:
            pass

        qs_cfs_for_image_type.update(marked_for_training=False)
        qs_cfs_for_image_type.update(training_complete=True)
        

def start(learners_findings, confirmed_findings_model, image_type_model, examinations_model):
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(train_chest_xray_model, 'interval', [learners_findings, confirmed_findings_model, image_type_model, examinations_model], hours=12)
    # scheduler.start()
    pass
