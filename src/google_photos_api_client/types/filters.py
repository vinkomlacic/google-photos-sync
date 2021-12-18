from enum import Enum
from typing import Optional, Sequence


__all__ = ['Filters', 'DateFilter', 'Date', 'DateRange', 'ContentFilter', 'ContentCategory', 'MediaTypeFilter',
           'MediaType', 'FeatureFilter', 'Feature']


class Date:
    """Represents a whole calendar date. Set day to 0 when only the month and year are significant, for example,
    all of December 2018. Set day and month to 0 if only the year is significant, for example, the entire of 2018.
    Set year to 0 when only the day and month are significant, for example, an anniversary or birthday.

    Unsupported: Setting all values to 0, only month to 0, or both day and year to 0 at the same time.
    """

    # Year of the date. Must be from 1 to 9999, or 0 to specify a date without a year.
    year: int

    # Month of a year. Must be from 1 to 12, or 0 to specify a year without a month and day.
    month: int

    # Day of month. Must be from 1 to 31 and valid for the year and month, or 0 if specifying a year/month where the
    # day isn't significant.
    day: int

    def __init__(self, date: dict):
        self.year = int(date['year'])
        if self.year < 0 or self.year > 9999:
            raise TypeError(f'{self.__class__.__name__}: Year must be in range of 1 to 9999, or 0 to specify a date '
                            f'without a year.')

        self.month = int(date['month'])
        if self.month < 0 or self.month > 12:
            raise TypeError(f'{self.__class__.__name__}: Month must be in range of 1 to 12, or 0 to specify a year '
                            f'without a month and day.')

        self.day = int(date['day'])
        if self.day < 0 or self.day > 31:
            raise TypeError(f"{self.__class__.__name__}: Day must be in range of 1 to 31, or 0 if specifying a "
                            f"year/month where day isn't significant.")

        all_values_are_zero = self.year == 0 and self.month == 0 and self.day == 0
        only_month_is_zero = self.year != 0 and self.month == 0 and self.day != 0
        day_and_year_are_both_zero = self.day == 0 and self.year == 0
        if all_values_are_zero or only_month_is_zero or day_and_year_are_both_zero:
            raise TypeError(f'{self.__class__.__name__}: Unsupported: Setting all values to 0, only month to 0, '
                            f'or both day and year to 0 at the same time.')


class DateRange:
    """Defines a range of dates. Both dates must be of the same format. For more information, see Date."""

    # The start date (included as part of the range) in one of the formats described.
    start_date: Date

    # The end date (included as part of the range). It must be specified in the same format as the start date.
    end_date: Date

    def __init__(self, date_range: dict):
        self.start_date = Date(date_range['startDate'])
        self.end_date = Date(date_range['endDate'])


class DateFilter:
    """This filter defines the allowed dates or date ranges for the media returned. It's possible to pick a set of
    specific dates and a set of date ranges."""

    # List of dates that match the media items' creation date. A maximum of 5 dates can be included per request.
    dates: Optional[Sequence[Date]]

    # List of dates ranges that match the media items' creation date. A maximum of 5 dates ranges can be included per
    # request.
    ranges: Optional[Sequence[DateRange]]

    def __init__(self, date_filter: dict):
        dates = date_filter.get('dates')
        self.dates = [Date(date) for date in dates] if dates else None
        if len(self.dates) > 5:
            raise TypeError(f'{self.__class__.__name__}: A maximum of 5 dates can be included per request.')

        ranges = date_filter.get('ranges')
        self.ranges = [DateRange(range) for range in ranges] if ranges else None
        if len(self.ranges) > 5:
            raise TypeError(f'{self.__class__.__name__}: A maximum of 5 date ranges can be included per request.')


class ContentCategory(Enum):
    """This is a set of pre-defined content categories that you can filter on."""

    # Default content category. This category is ignored when any other category is used in the filter.
    NONE = 'NONE'

    # Media items containing landscapes.
    LANDSCAPES = 'LANDSCAPES'

    # Media items containing receipts.
    RECEIPTS = 'RECEIPTS'

    # Media items containing cityscapes.
    CITYSCAPES = 'CITYSCAPES'

    # Media items containing landmarks.
    LANDMARKS = 'LANDMARKS'

    # Media items that are selfies.
    SELFIES = 'SELFIES'

    # Media items containing people.
    PEOPLE = 'PEOPLE'

    # Media items containing pets.
    PETS = 'PETS'

    # Media items from weddings.
    WEDDINGS = 'WEDDINGS'

    # Media items from birthdays.
    BIRTHDAYS = 'BIRTHDAYS'

    # Media items containing documents.
    DOCUMENTS = 'DOCUMENTS'

    # Media items taken during travel.
    TRAVEL = 'TRAVEL'

    # Media items containing animals.
    ANIMALS = 'ANIMALS'

    # Media items containing food.
    FOOD = 'FOOD'

    # Media items from sporting events.
    SPORT = 'SPORT'

    # Media items taken at night.
    NIGHT = 'NIGHT'

    # Media items from performances.
    PERFORMANCES = 'PERFORMANCES'

    # Media items containing whiteboards.
    WHITEBOARDS = 'WHITEBOARDS'

    # Media items that are screenshots.
    SCREENSHOTS = 'SCREENSHOTS'

    # Media items that are considered to be utility. These include, but aren't limited to documents, screenshots,
    # whiteboards etc.
    UTILITY = 'UTILITY'

    # Media items containing art.
    ARTS = 'ARTS'

    # Media items containing crafts.
    CRAFTS = 'CRAFTS'

    # Media items related to fashion.
    FASHION = 'FASHION'

    # Media items containing houses.
    HOUSES = 'HOUSES'

    # Media items containing gardens.
    GARDENS = 'GARDENS'

    # Media items containing flowers.
    FLOWERS = 'FLOWERS'

    # Media items taken of holidays.
    HOLIDAYS = 'HOLIDAYS'


class ContentFilter:
    """This filter allows you to return media items based on the content type. It's possible to specify a list of
    categories to include, and/or a list of categories to exclude. Within each list, the categories are combined with
    an OR.

    The content filter includedContentCategories: [c1, c2, c3] would get media items that contain (c1 OR c2 OR c3).
    The content filter excludedContentCategories: [c1, c2, c3] would NOT get media items that contain (c1 OR c2 OR
    c3). You can also include some categories while excluding others, as in this example: includedContentCategories:
    [c1, c2], excludedContentCategories: [c3, c4]

    The previous example would get media items that contain (c1 OR c2) AND NOT (c3 OR c4). A category that appears in
    includedContentCategories must not appear in excludedContentCategories.
    """

    # The set of categories to be included in the media item search results. The items in the set are ORed. There's a
    # maximum of 10 includedContentCategories per request.
    included_content_categories: Optional[Sequence[ContentCategory]]

    # The set of categories which are not to be included in the media item search results. The items in the set are
    # ORed. There's a maximum of 10 excludedContentCategories per request.
    excluded_content_categories: Optional[Sequence[ContentCategory]]

    def __init__(self, content_filter: dict):
        included_content_categories = content_filter.get('includedContentCategories')
        self.included_content_categories = [ContentCategory(content_category) for content_category
                                            in included_content_categories] if included_content_categories else None
        if len(self.included_content_categories) > 10:
            raise TypeError(f'{self.__class__.__name__}: There is a maximum of 10 included content categories per '
                            f'request.')

        excluded_content_categories = content_filter.get('excludedContentCategories')
        self.excluded_content_categories = [ContentCategory(content_category) for content_category
                                            in excluded_content_categories] if excluded_content_categories else None
        if len(self.excluded_content_categories) > 10:
            raise TypeError(f'{self.__class__.__name__}: There is a maximum of 10 excluded content categories per '
                            f'request.')


class MediaType(Enum):
    """The set of media types that can be searched for."""

    # Treated as if no filters are applied. All media types are included.
    ALL_MEDIA = 'ALL_MEDIA'

    # All media items that are considered videos. This also includes movies the user has created using the Google
    # Photos app.
    VIDEO = 'VIDEO'

    # All media items that are considered photos. This includes .bmp, .gif, .ico, .jpg (and other spellings), .tiff,
    # .webp and special photo types such as iOS live photos, Android motion photos, panoramas, photospheres.
    PHOTO = 'PHOTO'


class MediaTypeFilter:
    """This filter defines the type of media items to be returned, for example, videos or photos. Only one media type
    is supported. """

    # The types of media items to be included. This field should be populated with only one media type. If you
    # specify multiple media types, it results in an error.
    media_types: Sequence[MediaType]

    def __init__(self, media_type_filter: dict):
        self.media_types = [MediaType(media_type) for media_type in media_type_filter['mediaTypes']]
        if len(self.media_types) != 1:
            raise TypeError(f'{self.__class__.__name__}: Media types field must be populated with only one media type.')


class Feature(Enum):
    """The set of features that you can filter on."""

    # Treated as if no filters are applied. All features are included.
    NONE = 'NONE'

    # Media items that the user has marked as favorites in the Google Photos app.
    FAVORITES = 'FAVORITES'


class FeatureFilter:
    """This filter defines the features that the media items should have."""

    # The set of features to be included in the media item search results. The items in the set are ORed and may
    # match any of the specified features.
    included_features: Sequence[Feature]

    def __init__(self, feature_filter: dict):
        self.included_features = [Feature(feature) for feature in feature_filter['includedFeatures']]


class Filters:
    """The set of features to be included in the media item search results. The items in the set are ORed and may
    match any of the specified features. """

    # Filters the media items based on their creation date.
    date_filter: Optional[DateFilter]

    # Filters the media items based on their content.
    content_filter: Optional[ContentFilter]

    # Filters the media items based on the type of media.
    media_type_filter: Optional[MediaTypeFilter]

    # Filters the media items based on their features.
    feature_filter: Optional[FeatureFilter]

    # If set, the results include media items that the user has archived. Defaults to false (archived media items
    # aren't included).
    include_archived_media: Optional[bool]

    # If set, the results exclude media items that were not created by this app. Defaults to false (all media items
    # are returned). This field is ignored if the photoslibrary.readonly.appcreateddata scope is used.
    exclude_non_app_created_data: Optional[bool]

    def __init__(self, filters: dict):
        date_filter = filters.get('dateFilter')
        self.date_filter = DateFilter(date_filter) if date_filter else None

        content_filter = filters.get('contentFilter')
        self.content_filter = ContentFilter(content_filter) if content_filter else None

        media_type_filter = filters.get('mediaTypeFilter')
        self.media_type_filter = MediaTypeFilter(media_type_filter) if media_type_filter else None

        feature_filter = filters.get('featureFilter')
        self.feature_filter = FeatureFilter(feature_filter) if feature_filter else None

        include_archived_media = filters.get('includeArchivedMedia')
        self.include_archived_media = bool(include_archived_media) if include_archived_media else None

        exclude_non_app_created_data = filters.get('excludeNonAppCreatedData')
        self.exclude_non_app_created_data = bool(exclude_non_app_created_data) if exclude_non_app_created_data else None
