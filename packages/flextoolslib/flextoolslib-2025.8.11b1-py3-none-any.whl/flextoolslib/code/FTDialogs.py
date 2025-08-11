#
#   Project: FlexTools
#   Module:  FTDialogs
#   Platform: .NET Windows.Forms (Using python.NET 3)
#
#   General dialog functions for use by modules (e.g. for entering parameters
#   during a run.)
#
#   Copyright Craig Farrow
#   2025
#

from . import UIGlobal

from cdfutils.DotNet import (
    ChooserDialog,
    RadioDialog,
    TextDialog,
    )


# ------------------------------------------------------------------

def FTDialogChoose(title,
                   items, 
                   defaultItem=None):
        """
        Show a dialog with a dropdown menu for the user to choose from 
        a list of items.
        """

        dlg = ChooserDialog(title,
                            items,
                            defaultItem)

        dlg.Icon = UIGlobal.ApplicationIcon

        return dlg.Show()


def FTDialogRadio(title,
                  items, 
                  defaultItem=None):
        """
        Show a dialog with radio buttons for the user to choose from 
        a list of items.
        """

        dlg = RadioDialog(title,
                          items,
                          defaultItem)

        dlg.Icon = UIGlobal.ApplicationIcon

        return dlg.Show()


def FTDialogText(title,
                 defaultValue = ""):
        """
        Show a dialog for the user to enter a text value.
        """

        dlg = TextDialog(title,
                         defaultValue)

        dlg.Icon = UIGlobal.ApplicationIcon

        return dlg.Show()


def FTDialog(title,
             inputItems):
        """
        Show a dialog with multiple input items.
        inputItems is a list of tuples, (type, parameters) where,
            type is a value from FTDialog.InputTypeEnum, and
            parameters is an FTDialog.*Parameters object according to 
            the type of input field.
        
        Returns a list of selected values from the dialog (in order of
        the items), or None if the user canceled.
        """

        dlg = CustomDialog(title)
        dlg.Icon = UIGlobal.ApplicationIcon

        for t,p in inputItems:
            if t == InputTypeEnum.Separator:
                dlg.AddSeparator()

            elif t == InputTypeEnum.Choose:
                dlg.AddChooser(p.label, p.items, p.default)
                
            elif t == InputTypeEnum.Radio:
                dlg.AddRadio(p.label, p.items, p.default)

            elif t == InputTypeEnum.Text:               
                dlg.AddText(p.label, p.default)

            else:
                raise ValueError(f"{t} isn't a valid input item type!")


        return dlg.Show()
