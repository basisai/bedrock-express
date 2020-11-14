## BaseModel


### class bedrock_client.bedrock.model.BaseModel()
All `Models` served using Bedrock Express should inherit from `BaseModel`.


#### post_process(score: Union[List[str], List[float], List[int], List[Mapping[str, float]]], prediction_id: str)
Converts the output from predict() into a http response body, either as bytes or json.


* **Parameters**

    * **score** (*Union[List[str], List[float], List[int], List[Mapping[str, float]]]*) – The array of inference results returned from predict

    * **prediction_id** (*str*) – A generated id that can be used to look up this prediction



* **Returns**

    The http response body



* **Return type**

    Union[AnyStr, Mapping[str, Any]]



#### pre_process(http_body: AnyStr, files: Optional[Mapping[str, BinaryIO]] = None)
Converts http_body (or files) to something that can be passed into predict().
Typically, the result is an array of feature vectors.


* **Parameters**

    * **http_body** (*AnyStr*) – The serialized http request body

    * **files** (*Optional[Mapping[str, BinaryIO]]*, *defaults to None*) – A dictionary of field names to file handles



* **Returns**

    Array of feature vectors



* **Return type**

    List[List[float]]



#### abstract predict(features: List[List[float]])
Makes an inference using the initialised model.


* **Parameters**

    * **features** (*List[List[float]]*) – The array of feature vectors returned from pre_process



* **Returns**

    The array of inference results



* **Return type**

    Union[List[str], List[float], List[int], List[Mapping[str, float]]]



#### validate(skip_preprocess: bool = False, \*\*kwargs)
Validates the call chain: post_process(predict(pre_process(http_body)), prediction_id)
for any runtime error, including mismatched argument and return types, unsupported
serialisation format, etc.


* **Parameters**

    * **skip_preprocess** (*bool*) – Whether to skip checking the return value of pre_process
