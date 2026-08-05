"""Models definitions for the mysite application."""

from django.db import models


class BaseModel(models.Model):
    """Abstract base model with common fields."""

    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        """Meta information for BaseModel."""

        abstract = True


class Category(BaseModel):
    """Category model representing course categories."""

    id_category = models.AutoField("Category ID", primary_key=True)
    name = models.CharField("Name", max_length=40)

    class Meta:
        """Meta information for Category model."""

        db_table = "category"
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        """String representation of the Category model."""
        return self.name


class Institution(BaseModel):
    """Institution model representing educational institutions."""

    id_institution = models.AutoField("Institution ID", primary_key=True)
    name = models.CharField("Name", max_length=120)

    class Meta:
        """Meta information for Institution model."""

        db_table = "institution"
        verbose_name = "Institution"
        verbose_name_plural = "Institutions"

    def __str__(self):
        """String representation of the Institution model."""
        return self.name


class Formation(BaseModel):
    """Formation model representing educational formations."""

    id_formation = models.AutoField("Formation ID", primary_key=True)
    name = models.CharField("Name", max_length=100)
    workload = models.FloatField("Workload", null=True, blank=True)
    description = models.TextField("Description", null=True, blank=True)
    start_date = models.DateField("Start Date")
    end_date = models.DateField("End Date", null=True, blank=True)

    class Meta:
        """Meta information for Formation model."""

        db_table = "formation"
        verbose_name = "Formation"
        verbose_name_plural = "Formations"
        ordering = ["-end_date"]

    def __str__(self):
        """String representation of the Formation model."""
        return self.name


class Course(BaseModel):
    """Course model representing individual courses."""

    name = models.CharField("Name", max_length=60)
    workload = models.FloatField("Workload")
    description = models.TextField("Description", null=True, blank=True)
    curriculum_map = models.TextField("Curriculum Map", null=True, blank=True)
    start_date = models.DateField("Start Date")
    end_date = models.DateField("End Date", null=True, blank=True)
    is_active = models.BooleanField("Is Active", default=True)
    categories = models.ManyToManyField(Category, related_name="courses")
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True)
    formation = models.ManyToManyField(Formation, related_name="courses", blank=True)

    class Meta:
        """Meta information for Course model."""

        db_table = "course"
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ["-end_date"]

    def __str__(self):
        """String representation of the Course model."""
        return self.name


class Certification(BaseModel):
    """Certification model representing professional certifications (AWS, Databricks, etc.)."""

    name = models.CharField("Name", max_length=120)
    workload = models.FloatField("Workload", null=True, blank=True)
    description = models.TextField("Description", null=True, blank=True)
    credential_url = models.URLField("Credential URL", max_length=500, null=True, blank=True)
    credential_id = models.CharField("Credential ID", max_length=100, null=True, blank=True)
    issue_date = models.DateField("Issue Date")
    expiration_date = models.DateField("Expiration Date", null=True, blank=True)
    is_active = models.BooleanField("Is Active", default=True)
    categories = models.ManyToManyField(Category, related_name="certifications", blank=True)
    institution = models.ForeignKey(
        Institution,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="certifications",
    )

    class Meta:
        """Meta information for Certification model."""

        db_table = "certification"
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"
        ordering = ["-issue_date"]

    def __str__(self):
        """String representation of the Certification model."""
        return self.name
