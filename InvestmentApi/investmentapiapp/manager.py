from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None,role='investor', **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            role=role,
            **extra_fields
        )
        user.set_password(password)
        
        user.save(using=self._db)  
        return user
    
    def create_superuser(self, username, email, password=None, role='admin', **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        user = self.create_user(
            username=username,
            email=email,
            role=role,
            **extra_fields,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user