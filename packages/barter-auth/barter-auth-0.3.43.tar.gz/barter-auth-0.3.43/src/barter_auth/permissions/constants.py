
class STAFF_GROUPS:
    STAFF = 'staff'
    TOP_MANAGERS = "top_managers"
    BRANCH_ADVERTISERS = "branch_advertisers"
    BRANCH_BLOGGERS = "branch_bloggers"
    BRANCH_BOOKINGS = "branch_bookings"

    CHOICES_RU = (
        (STAFF, 'Сотрудники'),
        (TOP_MANAGERS, 'Топ менеджеры'),
        (BRANCH_ADVERTISERS, 'Сопровождение рекломодателей'),
        (BRANCH_BLOGGERS, 'Сопровождение блогеров'),
        (BRANCH_BOOKINGS, 'Сопровождение сделок'),
    )

class PERMS:
    USER_VIEW_ALL = "user_view_all"
    USER_NAME_AVATAR_EDIT = "user_name_avatar_edit"
    USER_SET_GROUP = "user_set_group"
    USER_SET_PERMS = "user_set_perms"
    USER_DATA_DWD = "user_data_dwd"

    ADV_VIEW_ALL = "adv_view_all"
    ADV_VIEW_ASSINED = "adv_view_assined"
    ADV_ADD = "adv_add"
    ADV_EDIT = "adv_edit"
    ADV_DELETE = "adv_delete"
    ADV_DATA_DWD = "adv_data_dwd"

    OFFER_VIEW_ALL = "offer_view_all"
    OFFER_VIEW_ASSINED = "offer_view_assined"
    OFFER_ADD = "offer_add"
    OFFER_EDIT_ALL = "offer_edit_all"
    OFFER_EDIT_ASSINED = "offer_edit_assined"
    OFFER_DELETE = "offer_delete"
    OFFER_DATA_DWD = "offer_data_dwd"

    BLOGGER_VIEW_ALL = "blogger_view_all"
    BLOGGER_VIEW_ASSINED = "blogger_view_assined"
    BLOGGER_EDIT_ALL = "blogger_edit_all"
    BLOGGER_EDIT_ASSINED = "blogger_edit_assined"
    BLOGGER_DATA_DWD = "blogger_data_dwd"

    BOOK_VIEW_ALL = "book_view_all"
    BOOK_VIEW_ASSINED = "book_view_assined"
    BOOK_EDIT_ALL = "book_edit_all"
    BOOK_EDIT_ASSINED = "book_edit_assined"
    BOOK_DELETE = "book_delete"
    BOOK_MODERATE_DONE_ALL = "book_moderate_done_all"
    BOOK_MODERATE_DONE_ASSINED = "book_moderate_done_assined"
    BOOK_DATA_DWD = "book_data_dwd"

    CHOICES_RU = (
        (USER_VIEW_ALL, 'Просмотр пользователей'),
        (USER_NAME_AVATAR_EDIT, 'Рерактирование имени/аватара'),
        (USER_SET_GROUP, 'Добавление в группу'),
        (USER_SET_PERMS, 'Назначение прав'),
        (USER_DATA_DWD, 'Скачивание'),

        (ADV_VIEW_ALL, 'Просмотр всех рекламодателей'),
        (ADV_VIEW_ASSINED, 'Просмотр своих рекламодателей'),
        (ADV_ADD, 'Добавление'),
        (ADV_EDIT, 'Редактирование'),
        (ADV_DELETE, 'Удаление (если возможно)'),
        (ADV_DATA_DWD, 'Скачивание данных'),

        (OFFER_VIEW_ALL, 'Просмотр всех товаров'),
        (OFFER_VIEW_ASSINED, 'Просмотр товаров своих рекламодателей'),
        (OFFER_ADD, 'Добавление'),
        (OFFER_EDIT_ALL, 'Редактирование'),
        (OFFER_EDIT_ASSINED, 'Редактирование своих'),
        (OFFER_DELETE, 'Удаление (если возможно)'),
        (OFFER_DATA_DWD, 'Скачивание данных'),

        (BLOGGER_VIEW_ALL, 'Просмотр блогеров'),
        (BLOGGER_VIEW_ASSINED, 'Просмотр своих блогеров'),
        (BLOGGER_EDIT_ALL, 'Редактирование (частичное)'),
        (BLOGGER_EDIT_ASSINED, 'Редактирование своих (частичное)'),
        (BLOGGER_DATA_DWD, 'Скачивание'),

        (BOOK_VIEW_ALL, 'Просмотр'),
        (BOOK_VIEW_ASSINED, 'Other'),
        (BOOK_EDIT_ALL, 'Редактирование всех (частичное)'),
        (BOOK_EDIT_ASSINED, 'Редактирование своих (частичное)'),
        (BOOK_DELETE, 'Other'),
        (BOOK_MODERATE_DONE_ALL, 'Модерация завершения всех сделок'),
        (BOOK_MODERATE_DONE_ASSINED, 'Модерация завершения своих сделок'),
        (BOOK_DATA_DWD, 'Скачивание'),
    )


__all__ = ['PERMS']