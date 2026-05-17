from enum import Enum

class UserRole (Enum): pass

class UserRole (Enum):

    VENDOR : int = 1 << 0
    CLIENT : int = 1 << 1
    VIDEO_CURATOR : int = 1 << 2
    DATA_COLLABORATOR : int = 1 << 3
    MODERATOR : int = 1 << 4
    MANAGER : int = 1 << 5

    ADMIN : int = 0b11111111

    def get_all_roles_list() -> list[UserRole]:
        """
        Get a list of all available roles.

        Returns
        -------
        list of UserRole
            All the roles available.
        """

        return [UserRole.VENDOR,
                UserRole.CLIENT,
                UserRole.VIDEO_CURATOR,
                UserRole.DATA_COLLABORATOR,
                UserRole.MODERATOR,
                UserRole.MANAGER]

    def from_sum(code: int) -> list[UserRole]:
        """
        Convert a bitmask to a list of roles.

        Parameters
        ----------
        code : int
            A bitmask representing the active roles.

        Returns
        -------
        list of UserRole
            The roles active in the bitmask.
        """
        
        for role in UserRole.get_all_roles_list():
            if code & role.value: yield role

    def from_strings(roles: list[str]) -> list[UserRole]:
        """
        Convert a list of strings to a list of roles.

        Parameters
        ----------
        roles : list of str
            A list of names for the active roles.

        Returns
        -------
        list of UserRole
            The roles present in the list.
        """

        for role in UserRole.get_all_roles_list():
            if role.name in roles: yield role

    def sum_roles(roles: list[UserRole]) -> int:
        """
        Sum a list of roles into a bitmask.

        Parameters
        ----------
        roles : list of UserRole
            Roles to convert.

        Returns
        -------
        int
            The bitmask representing the present roles as active.
        """

        rsum = 0
        for role in roles: rsum |= role.value
        return rsum

    def to_strings(roles: list[UserRole]) -> list[str]:
        """
        Convert a list of roles into a list of strings.

        Parameters
        ----------
        roles : list of UserRole
            Roles to convert.

        Returns
        -------
        list of str
            The list of strings representing the roles.
        """

        for role in roles: yield role.name
 
