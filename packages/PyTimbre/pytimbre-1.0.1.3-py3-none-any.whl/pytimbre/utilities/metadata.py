class AudioMetaData:
    """
    This class contains the various named elements of the audio that exist within the Wave file canonical descriptions
    of the elements of the List Chunk. This also provides methods to create the header for the StandardBinaryFile and
    the ListChunk for the Wave file.
    """

    def __init__(self):
        """
        Initialize the object
        """

        self._meta_data = dict()

    def __len__(self):
        return len(self._meta_data)

    @staticmethod
    def from_list_chunk(chunk):
        """
        This creates the class from the List Chunk class. It will populate the data from the properties of that object
        into the properties within this class.
        :param chunk: The List Chunk object to create the current project
        :type chunk: ListChunk
        :returns: AudioMetaData
        """

        obj = AudioMetaData()

        #   Loop through the properties of the ListChunk and insert the property values into the metadata dictionary
        for key in chunk.__dict__.keys():
            value = chunk.__dict__[key]

            if isinstance(value, dict):
                pass
            else:
                if value is not None:
                    obj._meta_data[key] = value

        return obj

    @staticmethod
    def from_header(header: dict):
        """
        This creates a class from the information within the header of the StandardBinaryFile. All elements are stored
        within the dictionary until the specific words are defined as the property names.
        :param header: the collection of information from the header of the StandardBinaryFile
        :type header: dict
        :return: The formatted metadata collection of information
        :rtype: AudioMetaData
        """

        obj = AudioMetaData()

        for key in header.keys():
            obj._meta_data[key] = header[key]

        return obj

    @staticmethod
    def from_standard_binary_file(path: str):
        """
        This function will read the header information from the file and create the information within this class
        based on the information within the binary file's header.
        :param path: the location of the standard binary file
        :type path: str
        :return: The header as a collection of metadata
        :rtype: AudioMetaData
        """

        #   Open the file for reading in binary format
        f_in = open(path, 'rb')

        #   Read the lines of header information
        name, value = AudioMetaData.convert_standard_binary_header(
            AudioMetaData.read_standard_binary_file_header_line(f_in)
        )

        #   This is the header line, so now we can determine how many total lines of header information is
        #   present in the file
        header_line_count = int(value)

        #   Read through the lines and extract the data as command and values that are inserted into a
        #   dictionary.
        header = dict()
        for i in range(header_line_count - 1):
            #   Split the data in the header line
            name, value = AudioMetaData.convert_standard_binary_header(
                AudioMetaData.read_standard_binary_file_header_line(f_in)
            )

            #   In effort to make the CSV representation of the data from the TimeHistory functions we need
            #   to ensure that the commas and extra carriage return/line feeds are removed.
            while ',' in name:
                name = name.replace(',', ';')
            while ',' in value:
                value = value.replace(',', ';')

            while '\r' in name:
                name = name.replace('\r', '')
            while '\r' in value:
                value = value.replace('\r', '')

            while '\n' in name:
                name = name.replace('\n', '')

            #   Assign the key and value within the dictionary
            header[name] = value

        return AudioMetaData.from_header(header), f_in

    @staticmethod
    def read_standard_binary_file_header_line(binary_file):
        """
        Python does not provide the ability to read a line of text from a
        binary file.  This function will read from the current position in the
        file to the new line character.  The set of bytes is then converted to
        a string and returned to the calling function.

        @author: frank Mobley

        Parameters
        ----------
        binary_file : FILE
            The file pointer that will be read from

        Returns
        -------
        The string representing a line of ASCII characters from the file.

        """

        #   Get the current position within the file so that we can return here
        #   after determining where the end of the file is.

        current_position = binary_file.tell()

        #   Find the end of the file

        binary_file.seek(-1, 2)

        eof = binary_file.tell()

        #   Return to the point we were within the file

        binary_file.seek(current_position, 0)

        #   Read until the last character is a new line or we have reached the
        #   end of the file.

        characters = ''
        char = ' '
        while ord(char) != 10 or binary_file.tell() == eof - 1:
            char = binary_file.read(1)
            if ord(char) != 10:
                characters += char.decode()

        return characters

    @staticmethod
    def convert_standard_binary_header(header_line: str):
        """
        This function will take the information within the header line and remove
        the semicolon in the front and all ellipsoid markers to determine the name
        of the property.  It also splits based on the colon to determine the value

        @author: Frank Mobley

        Parameters
        ----------
        header_line : STRING
            The line of text from the header of the file

        Returns
        -------
        name : STRING
            The name of the property or attribute

        value : STRING
            The value of the property

        """

        #   Split the string based on the colon

        elements = header_line.split(':')

        if len(elements) > 2:
            value = ':'.join(elements[1:])
        else:
            value = elements[1].strip()
        name = elements[0][1:].split('.')[0]

        return name, value

    @property
    def archival_location(self):
        if "archival_location" in self._meta_data.keys():
            return self._meta_data["archival_location"]
        else:
            return None

    @archival_location.setter
    def archival_location(self, archival_location):
        self._meta_data["archival_location"] = archival_location

    @property
    def artist(self):
        if "artist" in self._meta_data.keys():
            return self._meta_data["artist"]
        else:
            return None

    @artist.setter
    def artist(self, artist):
        self._meta_data["artist"] = artist

    @property
    def commissioned_organization(self):
        if "commissioned_organization" in self._meta_data.keys():
            return self._meta_data["commissioned_organization"]
        else:
            return None

    @commissioned_organization.setter
    def commissioned_organization(self, commissioned_organization):
        self._meta_data["commissioned_organization"] = commissioned_organization

    @property
    def general_comments(self):
        if "general_comments" in self._meta_data.keys():
            return self._meta_data["general_comments"]
        else:
            return None

    @general_comments.setter
    def general_comments(self, general_comments):
        self._meta_data["general_comments"] = general_comments

    @property
    def copyright(self):
        if "copyright" in self._meta_data.keys():
            return self._meta_data["copyright"]
        else:
            return None

    @copyright.setter
    def copyright(self, copyright):
        self._meta_data["copyright"] = copyright

    @property
    def creation_date(self):
        if "creation_date" in self._meta_data.keys():
            return self._meta_data["creation_date"]
        else:
            return None

    @creation_date.setter
    def creation_date(self, creation_date):
        self._meta_data["creation_date"] = creation_date

    @property
    def cropping_information(self):
        if "cropping_information" in self._meta_data.keys():
            return self._meta_data["cropping_information"]
        else:
            return None

    @cropping_information.setter
    def cropping_information(self, cropping_information):
        self._meta_data["cropping_information"] = cropping_information

    @property
    def originating_object_dimensions(self):
        if "originating_object_dimensions" in self._meta_data.keys():
            return self._meta_data["originating_object_dimensions"]
        else:
            return None

    @originating_object_dimensions.setter
    def originating_object_dimensions(self, originating_object_dimensions):
        self._meta_data["originating_object_dimensions"] = originating_object_dimensions

    @property
    def dots_per_inch(self):
        if "dots_per_inch" in self._meta_data.keys():
            return self._meta_data["dots_per_inch"]
        else:
            return None

    @dots_per_inch.setter
    def dots_per_inch(self, dots_per_inch):
        self._meta_data["dots_per_inch"] = dots_per_inch

    @property
    def engineer_name(self):
        if "engineer_name" in self._meta_data.keys():
            return self._meta_data["engineer_name"]
        else:
            return None

    @engineer_name.setter
    def engineer_name(self, engineer_name):
        self._meta_data["engineer_name"] = engineer_name

    @property
    def subject_genre(self):
        if "subject_genre" in self._meta_data.keys():
            return self._meta_data["subject_genre"]
        else:
            return None

    @subject_genre.setter
    def subject_genre(self, subject_genre):
        self._meta_data["subject_genre"] = subject_genre

    @property
    def key_words(self):
        if "key_words" in self._meta_data.keys():
            return self._meta_data["key_words"]
        else:
            return None

    @key_words.setter
    def key_words(self, key_words):
        self._meta_data["key_words"] = key_words

    @property
    def lightness_settings(self):
        if "lightness_settings" in self._meta_data.keys():
            return self._meta_data["lightness_settings"]
        else:
            return None

    @lightness_settings.setter
    def lightness_settings(self, lightness_settings):
        self._meta_data["lightness_settings"] = lightness_settings

    @property
    def originating_object_medium(self):
        if "originating_object_medium" in self._meta_data.keys():
            return self._meta_data["originating_object_medium"]
        else:
            return None

    @originating_object_medium.setter
    def originating_object_medium(self, originating_object_medium):
        self._meta_data["originating_object_medium"] = originating_object_medium

    @property
    def title(self):
        if "title" in self._meta_data.keys():
            return self._meta_data["title"]
        else:
            return None

    @title.setter
    def title(self, title):
        self._meta_data["title"] = title

    @property
    def color_palette_count(self):
        if "color_palette_count" in self._meta_data.keys():
            return self._meta_data["color_palette_count"]
        else:
            return None

    @color_palette_count.setter
    def color_palette_count(self, color_palette_count):
        self._meta_data["color_palette_count"] = color_palette_count

    @property
    def subject_name(self):
        if "subject_name" in self._meta_data.keys():
            return self._meta_data["subject_name"]
        else:
            return None

    @subject_name.setter
    def subject_name(self, subject_name):
        self._meta_data["subject_name"] = subject_name

    @property
    def description(self):
        if "description" in self._meta_data.keys():
            return self._meta_data["description"]
        else:
            return None

    @description.setter
    def description(self, description):
        self._meta_data["description"] = description

    @property
    def creation_software(self):
        if "creation_software" in self._meta_data.keys():
            return self._meta_data["creation_software"]
        else:
            return None

    @creation_software.setter
    def creation_software(self, creation_software):
        self._meta_data["creation_software"] = creation_software

    @property
    def data_source(self):
        if "data_source" in self._meta_data.keys():
            return self._meta_data["data_source"]
        else:
            return None

    @data_source.setter
    def data_source(self, data_source):
        self._meta_data["data_source"] = data_source

    @property
    def original_form(self):
        if "original_form" in self._meta_data.keys():
            return self._meta_data["original_form"]
        else:
            return None

    @original_form.setter
    def original_form(self, original_form):
        self._meta_data["original_form"] = original_form

    @property
    def digitizing_engineer(self):
        if "digitizing_engineer" in self._meta_data.keys():
            return self._meta_data["digitizing_engineer"]
        else:
            return None

    @digitizing_engineer.setter
    def digitizing_engineer(self, digitizing_engineer):
        self._meta_data["digitizing_engineer"] = digitizing_engineer

    @property
    def track_number(self):
        if "track_no" in self._meta_data.keys():
            return self._meta_data["track_no"]
        else:
            return -1

    @track_number.setter
    def track_number(self, track_number):
        self._meta_data["track_number"] = track_number

    @property
    def data_keys(self) -> list:
        return list(self._meta_data.keys())

    def add_field(self, field_name, field_value):
        """
        This will add a new field to the meta_data_information dictionary
        :param field_name: the name of the field, or the key
        :type field_name: str
        :param field_value: the value to assign
        :type field_value: Any
        """

        if field_name[0] != '_':
            self._meta_data[field_name] = field_value

    def field_present(self, field_name):
        """
        This examines the keys of the dictionary and determines whether this field already exists
        :param field_name: the name of the field to search the dictionary for
        :type field_name: str
        :return: whether the field_name exists within the dictionary keys
        :rtype: bool
        """

        return field_name in self.data_keys

    def get_field(self, field_name):
        return self._meta_data[field_name]

    def read_sample_rate(self, key):
        if key not in self.data_keys:
            raise ValueError(
                "The name of the sample rate element of the waveform is not located within the "
                "header dictionary. Please provide the correct name of the sample rate property"
            )
        else:
            return float(self.get_field(key))

    def read_start_time(self, key):
        from dateutil import parser

        if key not in self.data_keys and "TIME (TPM)" not in self.data_keys:
            raise ValueError(
                "The name of the start time element of the waveform is not located within the "
                "header dictionary. Please provide the correct name of the start time property"
            )
        elif "TIME (TPM)" in self.data_keys:
            return float(self.get_field('TIME (TPM)'))
        else:
            return parser.parse(self.get_field(key))

    def read_sample_count(self, key):
        if key not in self.data_keys:
            raise ValueError(
                "The number of samples must be provided, and the expected header element is not "
                "found within the list of objects in the header."
            )
        else:
            return int(self.get_field(key))

    def read_format(self, sample_format_key, data_format_key):
        if sample_format_key not in self.data_keys:
            raise ValueError(
                "The name of the sample format element of the waveform is not located within the "
                "header dictionary. Please provide the correct name of the sample format property"
            )
        else:
            if self.get_field(sample_format_key).upper() != "LITTLE ENDIAN":
                raise ValueError("The expected format is not present in the header.")

        if data_format_key not in self.data_keys:
            raise ValueError(
                "The name of the data format element of the waveform is not located within the "
                "header dictionary. Please provide the correct name of the data format property"
            )
        else:
            if self.get_field(data_format_key).upper() != "REAL*4":
                raise ValueError("The required sample formate is not present in the header.")



