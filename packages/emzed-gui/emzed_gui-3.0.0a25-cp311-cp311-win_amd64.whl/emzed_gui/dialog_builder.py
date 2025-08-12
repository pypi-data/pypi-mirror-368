# This file is part of emzed (https://emzed.ethz.ch), a software toolbox for analysing
# LCMS data with Python.
#
# Copyright (C) 2020 ETH Zurich, SIS ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.


import re
import string

import guidata.dataset.dataitems as di
import guidata.dataset.datatypes as dt
from guidata.dataset.qtwidgets import DataSetEditDialog
from guidata.utils import add_extension
from PyQt5.QtWidgets import QDialogButtonBox

di_FilesOpenItem_from_string = di.FilesOpenItem.from_string


def from_string(self, value):
    """patched version of method. look at

        guidata.dataset.dataitems.FilesOpenItem.from_string

    to understand what we are doing here"""

    # the original implementation has an eval() call which can
    # fail!
    try:
        return di_FilesOpenItem_from_string(self, value)
    except SyntaxError:
        # Syntax Error only can be triggered when given value looks
        # like a Python list of strings:
        return [add_extension(value.strip("\"'[]"))]


di.FilesOpenItem.from_string = from_string


# monkey patch following Items, else dt.DataSet.check() raises
# exceptions. They are assumed to be valid in any case:


def _translate_label_to_field_name(label):
    # translate label strings to python variable names
    invalid = r"""^°!"\§$%&/()=?´``+*~#'-.:,;<>|@$"""
    trtable = str.maketrans(invalid, " " * len(invalid))
    field_name = (
        label.lower()
        .translate(trtable)
        .replace("  ", " ")
        .replace("  ", " ")
        .replace(" ", "_")
    )
    try:
        exec("%s=0" % field_name) in dict()
    except Exception:
        raise ValueError(
            "converted label %r to field name %r "
            "which is not allowed in python" % (label, field_name)
        )
    return field_name


class _Stub(object):
    def __init__(self, item, to_wrap):
        self.item = item
        self.to_wrap = to_wrap

    def __call__(self, label, *a, **kw):
        # this function registers corresponding subclass of
        #    DataItem
        if not isinstance(label, str):
            raise ValueError("label must be a string")
        if not label:
            raise ValueError("you provided an empty label")
        if label[0] not in string.ascii_letters:
            raise ValueError("the first letter of the label must be a letter")

        fieldName = _translate_label_to_field_name(label)

        if self.item in (
            di.FilesOpenItem,
            di.FileOpenItem,
            di.FileSaveItem,
            di.DirectoryItem,
        ):
            if "notempty" in kw:
                kw["check"] = not kw["notempty"]
                del kw["notempty"]
            if "extensions" in kw:
                kw["formats"] = kw["extensions"]
                del kw["extensions"]

        dd = dict((n, v) for (n, v) in kw.items() if n in ["col", "colspan"])

        horizontal = kw.get("horizontal")
        if horizontal is not None:
            del kw["horizontal"]
        vertical = kw.get("vertical")
        if vertical is not None:
            del kw["vertical"]
        if "col" in kw:
            del kw["col"]
        if "colspan" in kw:
            del kw["colspan"]
        item = self.item(label, *a, **kw)
        if dd:
            item.set_pos(**dd)
        if horizontal:
            item.horizontal(horizontal)
        if vertical:
            item.vertical(vertical)

        # regiter item and fieldname
        self.to_wrap.items.append(item)
        self.to_wrap.fieldNames.append(fieldName)
        return self.to_wrap


def camel_to_snake_case(name):
    # https://stackoverflow.com/questions/1175208
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class DataHolder:
    def __init__(self, dd=None):
        if dd is not None:
            self.__dict__.update(dd)

    def update(self, ds):
        for key, value in ds.__dict__.items():
            if key.startswith("_DataSet"):
                continue
            if key.startswith("_") and not key.startswith("__"):
                setattr(self, key[1:], value)
            else:
                self[key] = value

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, name):
        return None

    def as_dict(self):
        return vars(self)


class DialogBuilder(object):
    # dynamic creation of __doc__
    _docStrings = []
    for _itemName, _item in di.__dict__.items():
        if _itemName.endswith("Item"):
            _docString = getattr(_item, "__doc__")
            if _docString is None:
                _docString = ""
            _dynamicMethodName = "        add_" + camel_to_snake_case(_itemName[:-4])
            _docStrings.append(_dynamicMethodName + "(...):\n" + _docString)

    __doc__ = "\n".join(_docStrings)

    def __init__(self, title="Dialog"):
        self.attrnum = 0
        self.title = title
        self.items = []
        self.instructions = []
        self.fieldNames = []
        self.buttonCounter = 0

        self.data = DataHolder()

    def __getattr__(self, name):
        """dynamically provides methods which start with "add...", eg
        "addInt(....)".

        If one calls

               b = Builder()
               b.addInt(params)

        then

               b.addInt

        is a stub function which is constructed and returned some
        lines below. Then

               b.addInt(params)

        calls this stub function, which registers the corresponding
        IntItem with the given params.

        """
        if not name.startswith("add_"):
            raise AttributeError("%r has no attribute '%s'" % (self, name))

        guidata_name = (
            "".join(part.capitalize() for part in name[4:].split("_")) + "Item"
        )
        if not hasattr(di, guidata_name):
            raise AttributeError("%r has no attribute '%s'" % (self, name))

        return self._get_stub(guidata_name, name)

    def _get_stub(self, guidata_name, name):
        item = getattr(di, guidata_name)
        stub = _Stub(item, self)

        # add docstring dynamically
        docString = getattr(item, "__doc__")
        docString = "" if docString is None else docString
        docString = "-\n\n" + name + "(...):\n" + docString
        stub.__doc__ = docString
        return stub

    def __dir__(self):
        items = [s[:-4].lower() for s in dir(di) if s.endswith("Item")]
        return ["add_instruction", "add_button", "show"] + [
            f"add_{item}" for item in items
        ]

    def add_instruction(self, what):
        self.instructions.append(what)
        return self

    def add_button(self, label, callback, check_other_fields_first=False, help=None):
        # the signature of 'wrapped' is dictated by the guidata
        # framework:
        def wrapped(ds, it, value, parent):
            if check_other_fields_first and not parent.check():
                return
            # check inputs before callback is executed
            self.data.update(ds)
            callback(self.data)

        # register ButtomItem in the same way other DataItem subclass
        # instances are registered in the "stub" function in
        # __getattr__:
        item_instance = di.ButtonItem(label, wrapped, help=help)
        self.items.append(item_instance)
        self.fieldNames.append("_button%d" % self.buttonCounter)
        self.buttonCounter += 1
        return self

    def show(self, ok_button="  Ok  ", cancel_button="Cancel", defaults=None):
        """opens the constructed dialog.

        In order to do so we construct sublcass of DataSet on the fly.

        the docstring of the class is the title of the dialog,
        class level attributes are instances of sublcasses of
        DataItem, eg IntItem.

        For more info see the docs of guidata how those classes
        are declared to get the wanted dialog.

        """
        from emzed_gui import qapplication

        app = qapplication()  # noqa: F841

        # put the class level attributes in a dict
        attributes = dict(zip(self.fieldNames, self.items))

        if defaults is not None:
            assert isinstance(defaults, dict)
            assert all(
                k in attributes for k in defaults.keys()
            ), "invalid key in defaults dict"

            for key, value in defaults.items():
                attributes[key]._default = value

                # quick and dirty check for type of current default value. guidata
                # has no clear API for this and wrong types raise excpetions from
                # PyQt widgets. And this apparently is the only way to figure out
                # which default value causes the problem.

                # construct class "Dialog" which is a sublcass of "dt.DataSet"
                # with the  given attributes:
                clz = type("Dialog", (dt.DataSet,), attributes)
                # as said: the docstring is rendered as the dialogues title:
                clz.__doc__ = self.title + "\n" + "\n".join(self.instructions)
                instance = clz()
                try:
                    win = DataSetEditDialog(instance)
                except Exception:
                    raise ValueError(
                        f"type of default value for {key} does not match"
                    ) from None

        clz = type("Dialog", (dt.DataSet,), attributes)
        # as said: the docstring is rendered as the dialogues title:
        clz.__doc__ = self.title + "\n" + "\n".join(self.instructions)
        instance = clz()
        win = DataSetEditDialog(instance)
        win.bbox.clear()

        if ok_button is not None:
            win.bbox.addButton(ok_button, QDialogButtonBox.AcceptRole)

        if cancel_button is not None:
            win.bbox.addButton(cancel_button, QDialogButtonBox.RejectRole)

        accepted = win.exec_()

        for name in self.fieldNames:
            if name.startswith("_button"):
                continue
            self.data.__dict__[name] = attributes[name].get_value(instance)

        if accepted == 0:
            return None
        return self.data
