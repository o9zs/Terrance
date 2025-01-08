from discord import Embed
Embed()
class Success(Embed):
	def __init__(self, *, title: str, description: str=None):
		super().__init__(
			title=f":white_check_mark: {title}",
			description=description,
			color=0x77b255
		)

class Error(Embed):
	def __init__(self, *, title: str, description: str=None):
		super().__init__(
			title=f":x: {title}",
			description=description,
			color=0xdd2e44
		)

class Warning(Embed):
	def __init__(self, *, title: str, description: str=None):
		super().__init__(
			title=f":warning: {title}",
			description=description,
			color=0xfecb4d
		)
		
__all__ = ["Success", "Error", "Warning"]