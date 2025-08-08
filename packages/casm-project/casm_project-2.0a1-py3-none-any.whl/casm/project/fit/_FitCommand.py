from typing import TYPE_CHECKING

from ._FittingData import FittingData

if TYPE_CHECKING:
    from casm.project import Project


class FitCommand:
    """Holds fitting data"""

    def __init__(self, proj: "Project"):
        self.proj = proj
        """casm.project.Project: CASM project."""

    def all(self):
        """Return the identifiers of all fits

        Returns
        -------
        all_fit: list[str]
            A list of fit identifiers
        """
        return self.proj.dir.all_fit()

    def list(self):
        """Print all fits"""
        for id in self.all():
            fitting_data = self.get(id)
            print(fitting_data)

    def get(self, id: str):
        """Load fitting data

        Parameters
        ----------
        id : str
            The fit identifier

        Returns
        -------
        fitting_data: FittingData
            The fitting data
        """
        return FittingData(proj=self.proj, id=id)

    def remove(self, id: str):
        """Remove fitting data

        Parameters
        ----------
        id : str
            The fit identifier
        """
        import shutil

        fit_dir = self.proj.dir.fit_dir(id)
        if not fit_dir.exists():
            raise FileNotFoundError(f"Fit {id} does not exist.")
        shutil.rmtree(self.proj.dir.fit_dir(id))

    def copy(self, src_id: str, dest_id: str):
        """Copy fitting data

        Parameters
        ----------
        src_id : str
            The source fit identifier
        dest_id : str
            The destination fit identifier
        """
        data = self.get(src_id)
        data.id = dest_id

        fit_dir = self.proj.dir.fit_dir(dest_id)
        fit_dir.mkdir(parents=True, exist_ok=False)
        data.fit_dir = fit_dir
        data.commit()
