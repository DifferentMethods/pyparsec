import httplib2
from iso8601 import iso8601
import json


class ParseAPI(object):
    reservedWords = "objectId", "updatedAt", "createdAt"

    def __init__(self, applicationId, restKey):
        self.url = 'https://api.parse.com/1'
        self.applicationId = applicationId
        self.restKey = restKey
        self.http = httplib2.Http(".pyparsec")

    def request(self, method, path, data=None):
        url = self.url + path
        headers = {
            "Content-Type": "application/json",
            "X-Parse-Application-Id": self.applicationId,
            "X-Parse-REST-API-Key": self.restKey,
        }
        body = None
        if data is not None:
            for i in ParseAPI.reservedWords:
                data.pop(i, None)
            body = json.dumps(data)
        response, content = self.http.request(url, method, headers=headers, body=body)
        obj = json.loads(content)
        return obj

    def pointer(self, instance):
        return {
            "__type":"Pointer",
            "className": instance.__class__.__name__,
            "objectId": instance.objectId
        }


    def list(self, class_):
        path = "/classes/" + class_.__name__
        obj = api.request("GET", path)
        return (class_.Construct(i, self, path) for i in obj["results"])

    def get(self, class_, objectId):
        path = "/classes/" + class_.__name__ + "/" + objectId
        obj = api.request("GET", path)
        return class_.Construct(obj, self, path)
        

    def create(self, class_, attributes=None):
        if attributes is None: attributes = {}
        path = "/classes/" + class_.__name__
        obj = api.request("POST", path, attributes)
        obj.update(attributes)
        return class_.Construct(obj, self, path)



class ParseObject(object):
    def __init__(self, attributes=None):
        if attributes is None:
            attributes = {}
        self.attributes = attributes
    
    def __repr__(self):
        return self.__class__.__name__ + ": " + repr(self.attributes)

    @classmethod
    def Construct(class_, attributes, api, url):
        self = class_(attributes)
        self._api = api
        self.objectId = attributes.get("objectId", None)
        if "createdAt" in attributes:
            self.createdAt = iso8601.parse_date(attributes.get("createdAt"))
        if "updatedAt" in attributes:
            self.updatedAt = iso8601.parse_date(attributes.get("updatedAt"))

        self._url = url + "/" + self.objectId
        return self

    def save(self):
        updates = self._api.request("PUT", self._url, self.attributes)
        self.attributes.update(updates)

    def delete(self):
        self._api.request("DELETE", self._url)


class Entity(ParseObject):
    def add_component(self, name, componentClass, attributes=None):
        component = self._api.create(componentClass, attributes)
        self.attributes[name] = self._api.pointer(component)
        component.entity = self
        return component

    def get_component(self, name, class_):
        pointer = self.attributes[name]
        component = self._api.get(class_, pointer["objectId"])
        component.entity = self
        return component

    def delete_component(self, name):
        self.attributes[name] = None

        
        

class Component(ParseObject):
    pass

class Threeper(Component):
    pass

if __name__ == "__main__":
    api = ParseAPI("WHwa1hKp2QrqCINgZKR8fLFXnruZaoiH0Agelf5A", "0X006tVJBFBpQlGVHYUJCOeFTWK46O9QsncEkfAe")
    for i in api.list(Entity):
        i.save()
        i.delete()
    e = api.create(Entity, dict(description="Xyzzy"))
    print e.add_component("thingo", Threeper)
    print e.get_component("thingo", Threeper)
    e.save()




