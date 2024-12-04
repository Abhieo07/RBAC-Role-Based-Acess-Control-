# Project Management System with Role-Based Access Control (RBAC)

## Overview

This project is a **Django-based Project Management System** designed to streamline task assignments and team management. It includes **Role-Based Access Control (RBAC)**, ensuring secure and hierarchical access to functionality. It integrates two main apps: 

- **account**: Handles user authentication, registration, OTP verification, and role assignments using jwt authentication.  
- **project**: Manages project creation, and role-specific project interactions.

---

## Key Features

### Account App
- **User Registration & Login**:
  - Users register with their email, name, and password.
  - Login ensures credentials are authenticated.
- **OTP Verification**:
  - Upon registration, users receive a 6-digit OTP for email verification.
- **Role Assignments**:
  - Roles (`Admin`, `Manager`, `Member`) are assigned via Django Groups.
  - Permissions like creating, editing, and viewing projects are mapped to these roles.
  
### Project App
- **Project Management**:
  - Users can create and manage projects depending on their role.
- **Task Assignments**:
  - Managers assign member who can access particular project.
- **Role-Based Access**:
  - `Admin`: Full control over all projects, users, and roles.
  - `Project Manager`: Create projects and manage their team.
  - `Project Member`: View assigned projects.
  -  `Team leader`: has no access to project since they interacts with users.

---

## API Endpoints

### Account App
| Endpoint              | HTTP Method | Description                                                                 |
|-----------------------|-------------|-----------------------------------------------------------------------------|
| `/api/register`       | `POST`      | Handles user registration and triggers OTP generation.                      |
| `/api/login`          | `POST`      | Authenticates users based on email and password.                            |
| `/api/verify`         | `POST`      | Verifies the OTP sent to the user's email.                                  |
| `/api/resend`         | `POST`      | Resends the OTP for email verification.                                     |


---

## Role-Based Access Control (RBAC)

RBAC is implemented using **Django Groups** and **Permissions**. Each group is mapped to specific permissions:

### Roles and Permissions

1. **Admin**:
   - Can manage all users, assign roles, and access all projects.
   - Permissions:
     - `auth.change_user`, `auth.add_user`
     - `project.add_project`, `project.delete_project`

2. **Project Manager**:
   - Can create and manage projects and team members.
   - Permissions:
     - `project.add_project`, `project.change_project`, `project.view_project`

3. **Project Member**:
   - Limited to viewing and participating in assigned projects.
   - Permissions:
     - `project.view_project`

4. **Team Leader**:
   - Can view users only 

Permissions are enforced using `PermissionRequiredMixin` decorators in views and APIs.

---

## Workflow: User Experience

1. **Registration and Login**:
   - A new user registers via the `/register` endpoint.
   - An OTP is sent to their email for verification.
   - Upon verification, the user is assigned a default role (`Member`).

2. **Role Assignment**:
   - Admin can assign roles (`Admin`, `Manager`, `Member`) via the admin panel or API.

3. **Project Management**:
   - **Manager** creates projects, assigns members, and manages tasks.
   - **Members** can view and contribute to assigned projects.

4. **Access Control**:
   - Every API and view checks the user’s role and permissions.
   - For example:
     - A `Member` trying to create a project will receive a "Permission Denied" error.
     - Only an `Admin` can remove a manager from a project.

---

## Project Structure

```plaintext
vrv/
├── account/
│   ├── models.py       # User models with custom manager
│   ├── views.py        # Authentication, OTP, and role assignment APIs
│   ├── forms.py        # User registration, login, and OTP forms
│   └── templates/      # Registration, login, and OTP templates
├── project/
│   ├── models.py       # Project and task models
│   ├── views.py        # Project creation, assignment, and management APIs
│   ├── templates/      # Project-related templates
├── manage.py
├── requirements.txt    # Project dependencies
└── README.md           # This file
```

## Installation
```link
git clone https://github.com/Abhieo07/RBAC-Role-Based-Acess-Control-
```
```
pip install -r requirements.txt
```
```
python manage.py setup_roles
```
```
python manage.py runserver
```

## Predefined User Credentials 
| Group                 | Email                                                                |Password            |
|-----------------------|-------------|-----------------------------------------------------------------------------|
| Admin                 | `admin@admin.com`                                                    |`gw8U@zn2SnW8$B"`   |
| Project Manager       | `user@manager.com` ,`jackdj059@gmail.com`                            |`gw8U@zn2SnW8$B"`   |
| Project Member        | `user@member.com` ,`gautamsagarrana11.com`                           |`gw8U@zn2SnW8$B"`   |
| Team Leader           | `user@leader.com`                                                    |`gw8U@zn2SnW8$B"`   |


## smtp 

  In `settings.py` do the following changes
    
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_USE_TLS = True
    EMAIL_PORT = 587
    EMAIL_HOST_USER = "`**your@gmail.com**`"
    EMAIL_HOST_PASSWORD = "`**yourAppPassword*`*"

