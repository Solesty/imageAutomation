from channels.layers import get_channel_layer


async def updateGalleryTimer(newSeconds):
    """
    Notify the UI of any new event as regards the
    default album, such as image upload and
    change in default album.
    """

    channel_layer = get_channel_layer()
    group_name = "album_view"
    content = {
        # This "type" passes through to the front-end to facilitate
        # our Redux events.
        "type": "UPDATE_GALLERY_TIMER",
        "payload": {"new_seconds": newSeconds},
    }

    await channel_layer.group_send(group_name, {
        # This "type" defines which handler on the Consumer gets
        # called.
        "type": "notify",
        "content": content,
    })


async def updateDefaultAlbum(albumPK):
    """
    Notify the UI of any new event as regards the
    default album, such as image upload and
    change in default album.
    """

    channel_layer = get_channel_layer()
    group_name = "album_view"
    content = {
        # This "type" passes through to the front-end to facilitate
        # our Redux events.
        "type": "UPDATE_DEFAULT_ALBUM",
        "payload": {"album_id": albumPK},
    }

    await channel_layer.group_send(group_name, {
        # This "type" defines which handler on the Consumer gets
        # called.
        "type": "notify",
        "content": content,
    })
