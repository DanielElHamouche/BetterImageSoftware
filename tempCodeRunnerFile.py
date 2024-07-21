)*zoom_scale)
heightratio = view.height()/(pixmap.height()*zoom_scale)
if view_ratio < image_ratio:
    zoom_scale *= widthratio
    view.scale(widthratio, widthratio)
else:
    zoom_scale *= heightratio
    view.scale(heightratio, heightratio)