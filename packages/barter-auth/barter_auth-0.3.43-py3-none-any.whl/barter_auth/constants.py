

class Role:
    ADVERTISER = -1
    INSTAGRAM = 1
    PARTNER = 100
    GROUP_PAYER = 200

    ANONYMOUS = 900

    CHOICES = [
        (INSTAGRAM, 'Instagram'),
        (ADVERTISER, 'Advertiser'),
        (PARTNER, 'Partner'),
        (GROUP_PAYER, 'Group payer')
    ]

class BloggerCategory:
    FOOD = 0
    AUTO = 1
    ANIMALS = 2
    ENTERTAINMENT = 3
    RECREATION = 4
    CLOTHES = 5
    BEAUTY = 6
    SPORT = 7
    CHILD = 8
    TRAVEL = 9
    OTHER = 100

    CHOICES = [
        (FOOD, 'Food'),
        (AUTO, 'Auto'),
        (ANIMALS, 'Animals'),
        (ENTERTAINMENT, 'Entertainment'),
        (RECREATION, 'Recreation'),
        (CLOTHES, 'Clothes'),
        (BEAUTY, 'Beauty'),
        (SPORT, 'Sport'),
        (CHILD, 'Child'),
        (TRAVEL, 'Travel'),
        (OTHER, 'Other'),
    ]