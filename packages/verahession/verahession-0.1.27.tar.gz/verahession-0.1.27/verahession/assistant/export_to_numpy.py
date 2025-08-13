import torch
import pickle
from .model import NeuralNet

def export_to_numpy(torch_path, numpy_path):
    data = torch.load(torch_path)

    model = NeuralNet(data["input_size"], data["hidden_size"], data["output_size"])
    model.load_state_dict(data["model_state"])
    model.eval()

    W1 = model.l1.weight.detach().numpy().T
    b1 = model.l1.bias.detach().numpy().reshape(1, -1)
    W2 = model.l2.weight.detach().numpy().T
    b2 = model.l2.bias.detach().numpy().reshape(1, -1)

    numpy_data = {
        "W1": W1,
        "b1": b1,
        "W2": W2,
        "b2": b2,
        "all_words": data["all_words"],
        "tags": data["tags"]
    }

    with open(numpy_path, "wb") as f:
        pickle.dump(numpy_data, f)

    print(f"[VERA] Exported weights to {numpy_path}")

# Example usage:
# export_to_numpy("model.pth", "model.pkl")
