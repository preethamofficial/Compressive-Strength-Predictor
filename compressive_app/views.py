from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
import numpy as np
import re
import json
from . import model as ann_model

def index(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            return HttpResponseBadRequest("Invalid JSON")

        ctm_raw = payload.get("ctm_values", "")
        if isinstance(ctm_raw, list):
            try:
                ctm_values = [float(x) for x in ctm_raw]
            except (TypeError, ValueError):
                return JsonResponse({"error": "Invalid numeric values in list"}, status=400)
        else:
            float_re = r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?"
            matches = re.findall(float_re, str(ctm_raw))
            if not matches:
                return JsonResponse({"error": "No numeric CTM values found"}, status=400)
            try:
                ctm_values = [float(x) for x in matches]
            except ValueError:
                return JsonResponse({"error": "Could not convert extracted tokens to floats"}, status=400)

        # parse number of future predictions
        try:
            num_predictions = int(payload.get("num_predictions", 0))
        except (TypeError, ValueError):
            num_predictions = 0

        # prepare input for model
        arr = np.array(ctm_values, dtype=float)
        # try several common model APIs
        predictions = None
        try:
            # 1) ann_model exposes a helper function predict_future(values, n)
            if hasattr(ann_model, "predict_future"):
                predictions = ann_model.predict_future(arr, num_predictions)
            # 2) ann_model.predict(values, n) style
            elif hasattr(ann_model, "predict"):
                try:
                    predictions = ann_model.predict(arr, num_predictions)
                except TypeError:
                    # maybe predict expects a batch array
                    predictions = ann_model.predict(arr.reshape(1, -1))
            # 3) ann_model provides a keras-like model object
            elif hasattr(ann_model, "model"):
                keras_model = ann_model.model
                inp = arr.reshape(1, -1)
                raw_preds = keras_model.predict(inp)
                # flatten to list and, if necessary, compute future steps externally
                predictions = np.ravel(raw_preds).tolist()
            else:
                return JsonResponse({"error": "No prediction function found in ann_model"}, status=500)

            # ensure predictions is a plain python list of floats
            if isinstance(predictions, np.ndarray):
                predictions = predictions.tolist()
            elif not isinstance(predictions, list):
                # try to coerce
                predictions = list(predictions)

            # return only the requested number of prediction values (or all if num_predictions <= 0)
            if num_predictions and num_predictions > 0:
                out = predictions[:num_predictions]
            else:
                out = predictions

            # return a plain JSON array containing only the values
            return JsonResponse(out, safe=False)

        except Exception as e:
            return JsonResponse({"error": f"Prediction failed: {str(e)}"}, status=500)

        result = {
            "parsed_ctm": ctm_values,
            "predictions": predictions,
            "message": "Parsed and predicted successfully"
        }
        return JsonResponse(result)
    return render(request, "index.html")