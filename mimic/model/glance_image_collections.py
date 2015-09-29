"""
Model objects for glance images.
"""

from characteristic import attributes, Attribute
from json import dumps
from mimic.model.rackspace_images import (ImageStore, OnMetalImage)


@attributes(["tenant_id", "region_name", "clock"])
class RegionalGlanceCollection(object):
    """
    A collection of images, in a given region, for a given tenant.
    """
    def image_by_id(self, image_id):
        """
        Retrieve a :obj:`Image` object by its ID.
        """
        images_store = ImageStore.create_image_store(self.tenant_id)
        for image in images_store:
            if image.image_id == image_id:
                return image

    def list_images(self, region_name, tenant_id, absolutize_url, include_details):
        """
        Return a list of glance images.
        """
        images_store = ImageStore.create_image_store(tenant_id)
        images = []

        for image in images_store:
            if region_name != "IAD" and isinstance(image, OnMetalImage):
                continue
            else:
                images.append(image.detailed_json(False, absolutize_url))
        result = {"images": images, "schema": "/v2/schemas/images",
                  "first": "/v2/images?limit=1000"}

        return dumps(result)


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
