from argparse import ArgumentParser, BooleanOptionalAction, _SubParsersAction
from moulti.client import send_delete, send_to_moulti_and_handle_reply, send_no_none_to_moulti_and_handle_reply
from moulti.environ import pint
from ..abstractquestion.cli import add_abstractquestion_options, question_get_answer

COMMAND = 'inputquestion' # abridged 'iq' below

def add_cli_arguments(subparsers: _SubParsersAction) -> None:
	# moulti inputquestion:
	helpmsg = 'create and manage interactive questions with a single-line input field'
	iq_parser = subparsers.add_parser(COMMAND, help=helpmsg)
	iq_subparsers = iq_parser.add_subparsers(required=True)
	add_iq_commands(iq_subparsers)

def add_iq_commands(iq_subparsers: _SubParsersAction) -> None:
	# moulti inputquestion add
	iq_add_parser = iq_subparsers.add_parser('add', help='add a new input question to Moulti')
	iq_add_parser.set_defaults(func=send_to_moulti_and_handle_reply, command=COMMAND, action='add')
	iq_add_parser.add_argument('id', type=str, help='unique identifier')
	add_abstractquestion_options(iq_add_parser)
	add_inputquestion_options(iq_add_parser)

	# moulti inputquestion update
	iq_update_parser = iq_subparsers.add_parser('update', help='update an existing input question')
	iq_update_parser.set_defaults(func=send_no_none_to_moulti_and_handle_reply, command=COMMAND, action='update')
	iq_update_parser.add_argument('id', type=str, help='unique identifier')
	add_abstractquestion_options(iq_update_parser, none=True)
	add_inputquestion_options(iq_update_parser, none=True)

	# moulti inputquestion get-answer
	helpmsg = 'return the answer provided by the end user'
	iq_getanswer_parser = iq_subparsers.add_parser('get-answer', help=helpmsg)
	iq_getanswer_parser.set_defaults(func=question_get_answer, command=COMMAND, action='get-answer')
	iq_getanswer_parser.add_argument('id', type=str, help='unique identifier')
	iq_getanswer_parser.add_argument('--wait', '-w', action='store_true', help='wait until the answer is available')

	# moulti inputquestion delete
	iq_delete_parser = iq_subparsers.add_parser('delete', help='delete an existing input question')
	iq_delete_parser.set_defaults(func=send_delete, command=COMMAND, action='delete')
	iq_delete_parser.add_argument('id', type=str, nargs='+', help='unique identifier')

def add_inputquestion_options(parser: ArgumentParser, none: bool = False) -> None:
	parser.add_argument('--placeholder', default=None if none else '', help='placeholder')
	parser.add_argument('--value', default=None if none else '', help='value')
	parser.add_argument('--password', default=None if none else False, action=BooleanOptionalAction, help='whether to hide input')
	parser.add_argument('--max-length', default=None if none else 0, type=pint, help='input maximum length (0 to disable)')
	parser.add_argument('--restrict', default=None if none else '', help='Python regular expression to restrict input ("" to disable)')
