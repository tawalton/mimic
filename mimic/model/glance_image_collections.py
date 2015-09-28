"""
Model objects for glance images.
"""

from characteristic import attributes, Attribute
from json import dumps
from mimic.model.rackspace_images import OnMetalImage
from mimic.model.rackspace_images import (RackspaceWindowsImage, RackspaceArchImage,
                                          RackspaceCentOSPVImage, RackspaceCentOSPVHMImage,
                                          RackspaceCoreOSImage, RackspaceDebianImage,
                                          RackspaceFedoraImage, RackspaceFreeBSDImage,
                                          RackspaceGentooImage, RackspaceOpenSUSEImage,
                                          RackspaceRedHatPVImage, RackspaceRedHatPVHMImage,
                                          RackspaceUbuntuPVImage, RackspaceUbuntuPVHMImage,
                                          RackspaceVyattaImage, RackspaceScientificImage,
                                          RackspaceOnMetalCentOSImage, RackspaceOnMetalCoreOSImage,
                                          RackspaceOnMetalDebianImage, RackspaceOnMetalFedoraImage,
                                          RackspaceOnMetalUbuntuImage)


@attributes(["tenant_id", "region_name", "clock", Attribute("images_store", default_factory=list)])
class RegionalGlanceCollection(object):
    """
    A collection of images, in a given region, for a given tenant.
    """
    def image_by_id(self, image_id):
        """
        Retrieve a :obj:`Image` object by its ID.
        """
        self.create_image_store(self.tenant_id)
        for image in self.images_store:
            if image.image_id == image_id:
                return image

    def list_images(self, region_name, tenant_id, absolutize_url, include_details):
        """
        Return a list of glance images.
        """
        images_store = self.create_image_store(tenant_id)
        images = []

        for image in images_store:
            if region_name != "IAD" and isinstance(image, OnMetalImage):
                continue
            else:
                images.append(image.detailed_json(absolutize_url))
        result = {"images": images, "schema": "/v2/schemas/images",
                  "first": "/v2/images?limit=1000"}

        return dumps(result)

    def create_image_store(self, tenant_id):
        """
        Generates the data for each image in each image class
        """
        image_classes = [RackspaceWindowsImage, RackspaceArchImage, RackspaceCentOSPVImage,
                         RackspaceCentOSPVHMImage, RackspaceCoreOSImage, RackspaceDebianImage,
                         RackspaceFedoraImage, RackspaceFreeBSDImage, RackspaceGentooImage,
                         RackspaceOpenSUSEImage, RackspaceRedHatPVImage, RackspaceRedHatPVHMImage,
                         RackspaceUbuntuPVImage, RackspaceUbuntuPVHMImage, RackspaceVyattaImage,
                         RackspaceScientificImage, RackspaceOnMetalCentOSImage,
                         RackspaceOnMetalCoreOSImage, RackspaceOnMetalDebianImage,
                         RackspaceOnMetalFedoraImage, RackspaceOnMetalUbuntuImage]
        if len(self.images_store) < 1:
            for image_class in image_classes:
                for image, image_spec in image_class.images.iteritems():
                    image_name = image
                    image_id = image_spec['id']
                    minRam = image_spec['minRam']
                    minDisk = image_spec['minDisk']
                    image_size = image_spec['OS-EXT-IMG-SIZE:size']
                    image = image_class(image_id=image_id, tenant_id=tenant_id,
                                        image_size=image_size, name=image_name, minRam=minRam,
                                        minDisk=minDisk)
                    if 'com.rackspace__1__ui_default_show' in image_spec:
                        image.set_is_default()
                    self.images_store.append(image)
        return self.images_store

    def _add_image_to_store(self, image):
        """
        Add a new image to the images store
        """
        self.images_store.append(image)


@attributes(["tenant_id", "clock",
             Attribute("regional_collections", default_factory=dict)])
class GlobalGlanceCollection(object):
    """
    A :obj:`GlobalGlanceCollection` is a set of all the
    :obj:`RegionalGlanceCollection` objects owned by a given tenant.  In other
    words, all the image objects that a single tenant owns globally.
    """

    def collection_for_region(self, region_name):
        """
        Get a :obj:`RegionalFlavorCollection` for the region identified by the
        given name.
        """
        if region_name not in self.regional_collections:
            self.regional_collections[region_name] = (
                RegionalGlanceCollection(tenant_id=self.tenant_id, region_name=region_name,
                                         clock=self.clock))
        return self.regional_collections[region_name]
