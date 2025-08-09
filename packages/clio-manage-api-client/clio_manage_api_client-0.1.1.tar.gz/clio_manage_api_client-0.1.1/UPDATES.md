## 7/19/25 Update:
   - **Removed model api as submodule**
   - **Clio API Model Generator has been published to pypi and is available via:**
      - pip install clio-api-model-generator

## 6/17/25:
   - **Updated JSON to newest version in model generator**
   - **Generated new models with updated API definitions**

## 4/9/25:
   ### Database
   - Tables seem to update themselves on the first request of the new model but to be on the safe side, create a copy before updating the client

## 3/13/25:
   ### Database
   - Database backup disabled by default. To enable, pass "store_responses=True" when initializing the client
   - Without database backup results can't be exported to an xlsx file
   
   ### Model Generation Sub-Module
   - **Disclaimer** : We are not affiliated with Clio or anyone on their development team. We're just working to help provide users with access to features that aren't directly available yet but can easily be achieved.
   - The Clio API is in active development. Changes are made regularly to the public API documentation that this client generates its models from
   - This client was developed specifically with this in mind so that the models are dynamically generated and can be updated without any changes to the code itself
   - The required models for this API client to run should be regenerated frequently, but we're aware of the issues that others are facing trying to set up the initial enviroment that aren't familiar with the Python programming language and how it's executed
   - Models have been added to the repository to skip the step of initializing the model generator and generating by the user themselves to hopefully ease the learning curve
   - The majority of endopoints are not effected by changes to Clio public documentation they provide but the models provided will likely be outdated shortly
   - Please submit any issues that you're having and we will gladly help you get setup.


## 3/4/25: 
- I was notified the database backup wasn't working correctly after the last commit that I tried to bypass the requirement. I've been working on a newer version that I'm getting ready to release but for now just run the following after installing the requirements:

```python
python clio-api-model-generator/generate_models.py 
python db/db_generator.py 
```

 ## 3/5/25 Update: 
 
- Added temp fix for sqlite database table generator.
- If issues continue, change line 129 in client.py to the following to completely remove it:
```python
python clio-api-model-generator/generate_models.py 
python db/db_generator.py 
self.response_handler = None
````