ROLE_OWNER = 1
ROLE_ADMIN = 2
ROLE_EDITOR = 3
ROLE_NONE = 4

REACTION_LIKE = 1
REACTION_DISLIKE = 2
REACTION_NONE = 3

ROLES = (
    (ROLE_OWNER, f'Owner'),
    (ROLE_ADMIN, f'Admin'),
    (ROLE_EDITOR, f'Editor'),
    (ROLE_NONE, f'None'),
)

REACTIONS = (
    (REACTION_LIKE, f'Like'),
    (REACTION_DISLIKE, f'Dislike'),
    (REACTION_NONE, f'None'),
)