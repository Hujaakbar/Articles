# Dependency Injection

![injection](./images/injection.jpg)

Dependency Injection often abbreviated as DI is a design pattern/programming technique or simply a term thrown around a lot in software development lingo. When I first encountered this term, I didn't understand what it meant since it seemed to mean something complicated. To my surprise it is just a fancy term representing a simple concept. Before going any further let's lay a groundwork and define some terms.

Service
: any class that contains some useful functionality.

Dependency
: a service (any class ) that is used by another class or function.
Let's say we have a web server with two classes: an authentication class and a database management class. Users can make a request to our web server to add new data or delete some data. On the server side, the database management class is responsible for connecting to database and modifying the data but it relies on authentication class to check if the user who is making the request is authenticated and has necessary privileges. For database management class, authentication class is a dependency because database management class depends on authentication class to to do its job.

Client
: a class that uses service (another class) as its dependency.
From out above web server example, database management class is considered a client. _A client can be a dependency to another class._

Code example:

```python

class AuthenticateUser:

    # some other code

    def isAuthenticated(self, request):
        return request.user != "AnonymousUser"


class SomeDatabaseConnector:
     # some other code

    def add_data(self, user, data_to_enter):
        # logic to connect to db and record the data
        return "data entered successfully"

class Database_Management:
    def __init__():
        self.authenticator = AuthenticateUser()
        self.database = SomeDatabaseConnector()

    # some other code

    def add_data(self, request, data):
        if self.authenticator.isAuthenticated(request):
            self.database.create(user=request.user, data_to_enter=data)
        else:
            return "User is not authenticated"

db = Database_Management()
# we don't dive deep into how we got request and user.
# it is usually provided by the web framework/library.
db.add_data(request, user)
```

## What is Dependency Injection

Now we have some idea about what dependencies and clients are. It is time to define "Dependency Injection". Dependency Injection is passing an already created object as an argument to another function/class instead of creating it in the body of that client class/function. If my definition didn't make much sense, here is the alternative definitions by [Wikipedia](https://en.wikipedia.org/wiki/Dependency_injection) "Dependency injection is a programming technique in which an object or function receives other objects or functions that it requires, as opposed to creating them internally".

One example is worth dozens of definitions, isn't it? I hear you. So below is the example we used earlier this time with dependencies being injected.

```python

class AuthenticateUser:

    # some other code

    def isAuthenticated(self, request):
        return request.user != "AnonymousUser"


class SomeDatabaseConnector:
     # some other code

    def add_data(self, user, data_to_enter):
        # logic to connect to db and record the data
        return "data entered successfully"

class Database_Management:
    def __init__(authentication_class, database_connector_class):
        self.authenticator = authentication_class
        self.database = database_connector_class

    # some other code

    def add_data(self, request, data):
        if self.authenticator.isAuthenticated(request):
            self.database.create(user=request.user, data_to_enter=data)
        else:
            return "User is not authenticated"


auth_class = AuthenticateUser()
db_connector_class = SomeDatabaseConnector()

# Pay attention here
# we are INJECTING (passing) dependencies to the client Database_Management class
db = Database_Management(auth_class, db_connector_class)
# we don't dive deep into how we got request and user.
# it is usually provided by the web framework/library.
db.add_data(request, user)
```

You might ask what is the purpose of injecting dependencies in this way. After all with the above example it doesn't look that impressive, right? What is the difference between initializing the dependencies inside the client versus passing them as arguments to the client?

Above example illustrates mechanics of dependency injection but not its benefits. Now let's talk about its benefits. Primary benefit is to keep various functions of a program loosely coupled. As this [StackOverflow answer](https://stackoverflow.com/a/4618417/22606938) excellently points out "the objects change more frequently then the code that uses them". If not loosely coupled, changes in one part of the program requires modification in multiple places. On the other hand, if loosely coupled, changes in one part of the program requires _ideally_ no modification in other parts of the program. In this regard, by injecting dependencies, i.e, passing already initialized objects as an argument rather than creating them internally, we can keep the creation and usage of the object separate. In this way client function/class doesn't need to know how to create the object or even which object it is using, it only needs to know how to use it. As long as you don't change the methods and fields of the object, your program continues to work without breaking even if you swap the dependencies or change the parameters of those dependencies. Dependency Injection also allows sharing state among client classes.

As an example let's imagine an app that allows users to set profile photos. Our app uses ASW S3 bucket (storage) to store user photos.

```python

class S3:
    def __init__():
        # AWS S3 specific code such as
        # using boto3, connect to s3 bucket

    def upload(self, data):
        # logic to upload the data
        return "link to the uploaded data"

class UserProfile:

    def __init__(cloud_storage):
        self.storage = cloud_storage

    # other code
    def profile_photo(self, user, photo):
        link = self.storage.upload(photo)
        # save the link to the database that points to this user
        return "successfully uploaded profile photo"

s3_bucket = S3()
user = UserProfile(s3_bucket)

user.profile_photo(request.user, photo)
```

After sometime we found out that Google Cloud offered cheaper storage solution. We decided to use Google Cloud Storage instead of AWS S3 to store new user profile photos.

```python

class Google_Storage:
    def __init__():
        # Google Storage specific code such as
        # different API and interface to connect to GCP storage

    def upload(self, data):
        # logic to upload the data
        return "link to the uploaded data"

class UserProfile:

    def __init__(cloud_storage):
        self.storage = cloud_storage

    # other code
    def profile_photo(self, user, photo):
        link = self.storage.upload(photo)
        # save the link to the database that points to this user
        return "successfully uploaded profile photo"

gcp_bucket = Google_Storage()
user = UserProfile(gcp_bucket)

user.profile_photo(request.user, photo)
```

As long as the storage service has the `upload` method that takes data as its argument and returns a link to uploaded data, `UserProfile` class does not care or even know which class it is using whether `S3` class or `Google_Storage` class. This comes handy in testing too. We can easily swap the dependency services with mocks to test the client.

**Note:** In real life entire logic of the application is not usually defined in single file. Besides, the code is much longer than the above examples.

Let's see another example in which client class is not concerned about how to initialize the dependency.

```python

class StorageClass:
    # hardcoded fields
    _cloud_provider = "AWS"
    _storage = "S3"
    _bucket_name = "my_bucket"

    # some other logic

    def upload(self, data):
        # connect to database
        # save the data
        return link_to_uploaded_data

    def delete(self, data_id):
        # connect to database
        # delete the data
        return "successfully deleted"


class FreemiumUser:

    def __init__(self, storage_class):
        self.storage = storage_class

    def replace_profile_photo(self, request, photo):
        # delete existing photo
        # compress the new photo and
        # upload it using the storage dependency class
        self.storage.delete(old_photo_id)
        self.storage.upload(new_compressed_photo)


class PremiumUsers:

    def __init__(self, storage_class):
        self.storage = storage_class

    # some other functionalities

    def add_profile_photo(self, request, photo):
        # instead of deleting existing photo
        # allow user to have more than one profile photo
        self.storage.upload(photo)

dependency = StorageClass()
freemium_users = FreemiumUser(dependency)
freemium_users.replace_profile_photo(request, photo)

premium_user = PremiumUser(dependency)
premium_user.add_profile_photo(request, photo)
```

In above code, we have a `StorageClass` dependency that is being used by `FreemiumUser` and `PremiumUsers` clients. Imagine it is a big application and several developers are responsible for different parts of the application. Web development team is among others responsible for `FreemiumUser` and `PremiumUsers` classes. You are responsible for `StorageClass` class.

In a hurry you hardcoded `StorageClass` fields. You know that it would be much better to change them to parameters. Since your team is using Dependency Injection and other classes only rely on methods not , you can easily change the `StorageClass` without impacting depending classes namely, `FreemiumUser` and `PremiumUsers` classes.

```python

class StorageClass:

    def __init(self, cloud_provide, storage_name, bucket_name)
        self.cloud_provider = cloud_provide
        self.storage = storage_name
        self.bucket_name = bucket_name

    # some other logic

    def upload(self, data):
        # connect to database
        # save the data
        return link_to_uploaded_data

    def delete(self, data_id):
        # connect to database
        # delete the data
        return "successfully deleted"


class FreemiumUser:

    def __init__(self, storage_class):
        self.storage = storage_class

    def replace_profile_photo(self, request, photo):
        # delete existing photo
        # compress the new photo and
        # upload it using the storage dependency class
        self.storage.delete(old_photo_id)
        self.storage.upload(new_compressed_photo)


class PremiumUsers:

    def __init__(self, storage_class):
        self.storage = storage_class

    # some other functionalities

    def add_profile_photo(self, request, photo):
        # instead of deleting existing photo
        # allow user to have more than one profile photo
        self.storage.upload(photo)

dependency = StorageClass(
    cloud_provide="AWS",
    storage_name="S3",
    bucket_name="my_bucket"
)
freemium_users = FreemiumUser(dependency)
freemium_users.replace_profile_photo(request, photo)

premium_user = PremiumUser(dependency)
premium_user.add_profile_photo(request, photo)
```

If you were **NOT** using dependency injection, i.e initializing `StorageClass` class inside client classes, the change would break `FreemiumUser` and `PremiumUsers` classes and you had to ask the maintainers of those classes to update the classes.

Another benefit of dependency injection is sharing state among clients. _It is similar to singleton concept_

```javascript
class DependencyClass {
    constructor() {
        this.isDataReady = false;
        this.data = null;
    }

    processData(data) {
        // Process data logic
        this.data = processed_data;
        return "done"
    }

    deleteAll() {
        // Delete all data
        this.data = null;
    }
}

class Client1 {
    constructor(dependencyClass) {
        this.dependency = dependencyClass;
    }

    async fetchData() {
        // Asynchronously fetch data
        const fetchedData = await this.FetchData();
        this.dependency.processData(fetchedData);
        this.dependency.isDataReady = true;
    }

}

class Client2 {
    constructor(dependencyClass) {
        this.dependency = dependencyClass;
    }

    consumeData() {
        // Check dependency.isDataReady every 10 seconds
        this.intervalId = setInterval(() => {
            if (this.dependency.isDataReady) {

                // use the the this.dependency.data

                // Stop checking once data is ready and consumed
                clearInterval(this.intervalId);
            }
        }, 10000); // 10 seconds
    }

    deleteData() {
        this.dependency.deleteAll();
        this.dependency.isDataReady = false;
    }
}

const dependency = new DependencyClass();
const client1 = new Client1(dependency);
const client2 = new Client2(dependency);

client1.fetchData();
client2.consumeData();

```

In above code, `Client1` and `Client2` classes use `DependencyClass`'s `is_data_ready` and `data` fields to share state, i.e to let interested parties know the state whether data is ready or not. `Client1` and `Client2` classes do not need to know each other's existence. They only communicate with `DependencyClass` class. `Client1` class is not concerned whether the data it fetches and assigns to `DependencyClass` class's field is used by one class or ten different classes. Likewise `Client2` class is not concerned with which class fetches data and how. It only communicates with `DependencyClass` class.

**Note:** you inject dependencies not only in constructors of the classes, but also via setter methods, and interfaces.

Example of setter injection:

```python
class Service:
    def do_something(self):
        print("Doing something in the service...")

class Client:
    def __init__(self):
        self._service = None

    def set_service(self, service: Service):
        """Injects the service dependency."""
        self._service = service

    def do_something_in_client(self):
        if self._service is not None:
            self._service.do_something()
        else:
            print("Service not injected!")

client = Client()
service = Service()
client.set_service(service)
client.do_something_in_client()
```

The point is, you don't necessarily need to inject dependency at the class (client) initialization. Using setter methods, you can inject dependencies after initializing the client class.

---

## Bonus section

Up until now we used python in our examples. Dependency injection is a concept/technique that can be implemented in almost all languages. Some languages have some nice shortcuts that make dependency injection even more concise. One of such languages is Typescript.

**Explicit way:**

```typescript

class DependencyClass(){
// class logic
}


class Client(){

    private dep: DependencyClass;

    constructor(Dependency: DependencyClass){
        this.dep = Dependency
    }
}

let dependency = new DependencyClass()
let client = new Client(dependency)

```

In this version, the constructor receives an instance of `DependencyClass` as an argument (Dependency).
The argument (Dependency) is then assigned to the dep property of the `Client` class.
This approach explicitly defines the `dep` property in `Client` class and assigns the parameter to it in the constructor.

**Shorthand:**

```typescript

class DependencyClass(){
// class logic
}


class Client(){

    constructor(private dep: DependencyClass)
    { }
}

let dependency = new DependencyClass()
let client = new Client(dependency)

```

This version uses TypeScript’s shorthand syntax for property declarations.
By adding the private keyword in the constructor parameter (`private dep: DependencyClass`), TypeScript automatically creates a private class property named `dep` and assigns the constructor argument to it.
There’s no need to explicitly declare and assign dep in the class body; TypeScript handles both in one step.

---

## Conclusion

Dependency Injection is a simple concept: passing a class object to another class as an argument. It is main benefit of separation of concerns such as dependency initialization and dependency usage. It becomes useful when you need to test your code or modify some parts of your code since it allows loose coupling.
