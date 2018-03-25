# domain-classification
Database &amp; API for classified domains. Project related to Infokaaos

## Installation

```
pip install --editable .
export FLASK_APP=flaskr.py
export FLASK_DEBUG=true
flask run
```

## API specs

### POST /add_category

Post parameters:
- name, mandatory
- parent_categories, should be in form "1, 2, 3" list of integers, not mandatory
- child_categories, should be in same form as above, not mandatory

### POST /add_domain

Post parameters:
- name, mandatory
- parent_category, for example 1, is parent category id. This should be category which doesn't have child categories! That's because every domain should be a leaf in category-domain tree. 

### GET /get_categories

### GET /get_domains



