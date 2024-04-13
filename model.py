import numpy as np
import onnxruntime as ort
from PIL import Image
from resizeimage import resizeimage
from logger import setup_logger

logger = setup_logger(__name__)

class Model:
    def __init__(self, onnx_path):
        self.model_path = onnx_path
        self.session = None
        self.load_model()

    def load_model(self):
        """Load the ONNX model."""
        try:
            self.session = ort.InferenceSession(self.model_path)
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def preprocess(self, inputImage):
        """Preprocess the image for ONNX inference."""
        try:
            img = resizeimage.resize_cover(inputImage, [224, 224], validate=False)
            img_ycbcr = img.convert('YCbCr')
            img_y, img_cb, img_cr = img_ycbcr.split()
            img_ndarray = np.asarray(img_y)

            img_normalized = np.expand_dims(np.expand_dims(img_ndarray, axis=0), axis=0).astype(np.float32) / 255.0
            return img_cb, img_cr, img_normalized
        except Exception as e:
            logger.error(f"Error during preprocessing: {e}")
            raise

    def predict(self, processed_image):
        """Run model prediction on the preprocessed image."""
        try:
            input_name = self.session.get_inputs()[0].name
            ort_inputs = {input_name: processed_image}
            ort_outs = self.session.run(None, ort_inputs)
            return ort_outs[0]
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise

    def postprocess(self, prediction, img_cb, img_cr):
        """Convert model output back to an image."""
        try:
            img_out_y = Image.fromarray((prediction[0] * 255.0).clip(0, 255).astype(np.uint8)[0], mode='L')
            final_img = Image.merge(
                "YCbCr", [
                    img_out_y,
                    img_cb.resize(img_out_y.size, Image.BICUBIC),
                    img_cr.resize(img_out_y.size, Image.BICUBIC),
                ]).convert("RGB")
            return final_img
        except Exception as e:
            logger.error(f"Postprocessing failed: {e}")
            raise

    def process_image(self, inputImage):
        """Entry method to process an image."""
        try:
            img_cb, img_cr, processed_image = self.preprocess(inputImage)
            predictions = self.predict(processed_image)
            logger.debug(f'Input shape: {processed_image.shape}, Output shape: {predictions.shape}')
            return self.postprocess(predictions, img_cb, img_cr)
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise

# Example Usage:
# model = Model('path_to_model.onnx')
# result = model.process_image(input_image)
