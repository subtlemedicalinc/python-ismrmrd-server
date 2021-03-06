
import ismrmrd
import os
import logging
import numpy as np

# Folder for debug output files
debugFolder = "/tmp/share/debug"


def groups(iterable, predicate):
    group = []
    for item in iterable:
        group.append(item)

        if predicate(item):
            yield group
            group = []


def conditional_groups(iterable, predicateAccept, predicateFinish):
    """
    Usage: conditional_groups(connection,
                            lambda acq: not acq.is_flag_set(ismrmrd.ACQ_IS_PHASECORR_DATA),
                            lambda acq: acq.is_flag_set(ismrmrd.ACQ_LAST_IN_SLICE))
    :param iterable: open connection receiving items
    :param predicateAccept: condition to accept item
    :param predicateFinish: condition to consider a group of items complete and start another group
    :return: yield groups
    """
    group = []
    try:
        for item in iterable:
            if item is None:
                break

            if predicateAccept(item):
                group.append(item)

            if predicateFinish(item):
                yield group
                group = []
    finally:
        iterable.send_close()


def process(connection, config, metadata):
    logging.info("Config: \n%s", config)
    logging.info("Metadata: \n%s", metadata)

    # TODO: validate the metadata here against the app schema that specifies parameters
    # at runtime: expect the parameters defined in the app schema to be in the metadata XML tree

    # TODO: determine how to check that images are of image type: Image
    # if using conditional groups --> could use something like this:
    # for group in conditional_groups(connection, lambda acq: acq.is_flag_set(ismrmrd.IMTYPE_IMAG), lambda acq: acq.is_flag_set(ismrmrd.ACQ_LAST_IN_SLICE)):
    # but needs a  way to check image type and not acquisition flag

    # see different image types here:
    # https://github.com/ismrmrd/ismrmrd-python/blob/80fecd03c29e0b53b2b86a796942b4076e971b1e/ismrmrd/constants.py#L63
    # TODO: determine if ismrmrd.ACQ_LAST_IN_SLICE is the correct flag for pixel data (and not Kspace lines)
    for group in groups(connection, lambda acq: acq.is_flag_set(ismrmrd.ACQ_LAST_IN_SLICE)):
        image = process_group(group, config, metadata)

        logging.debug("Sending image to client:\n%s", image)
        connection.send_image(image)


def process_group(group, config, metadata, debug=False):
    # Create folder, if necessary
    if debug and not os.path.exists(debugFolder):
        os.makedirs(debugFolder)
        logging.debug("Created folder " + debugFolder + " for debug output files")

    # Format data into single [cha RO PE] array
    data = [acquisition.data for acquisition in group]
    input_data = np.stack(data, axis=-1)

    if debug:
        logging.debug("Input data is size %s" % (input_data.shape,))
        np.save(debugFolder + "/" + "raw.npy", data)

    # call SubtleMR inference here
    output_data, output_metadata = dummy_subtle(input_data, metadata, config)

    # Format as ISMRMRD image data
    image = ismrmrd.Image.from_array(output_data, acquisition=group[0])
    image.image_index = 1

    # TODO: need to set meta attributes here (that will be used to create the output dicom files)

    return image


def dummy_subtle(input_data, metadata, config):
    pass
    # TODO: decide if need to return an ismrmrd Image instead of array
    # todo (to save Subtle processing info, & update acquisition matrix in SRE)
    output_metadata = metadata.copy()

    return input_data, output_metadata
