class PatchedLayer:
    def __init__(self, layer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patched_layer = layer

    def unpatch(self):
        return self.patched_layer
