"""
This contains everything in the Cost Effectiveness section.
"""
import streamlit as st
import numpy as np
import pandas as pd

# For writing formulae in the "Details" sections:
import utilities_lifetime.latex_equations as eqn


def main(
        df: pd.DataFrame,
        mrs_input: int,
        fixed_params: dict,
        table_cost_effectiveness: np.array,
        model_input_str: str
        ):
    """
    Main function for drawing everything under the "Resources" tab.

    This setup of picking bits out of dictionaries is inherited
    from the older version of this container that had all results
    stored in separate variable names. Maybe one day I'll tidy this.

    Inputs:
    -------
    df                       - pd.DataFrame. Contains all of the
                               calculated results for all mRS scores.
    mrs_input                - int. The mRS score to highlight in areas
                               that only show one score's results.
    fixed_params             - dict. Contains fixed parameters
                               independent of the model results.
    table_cost_effectiveness - np.array. The table of net benefit by
                               change in outcome, ready to print.
    model_type_used          - str. Whether this is the separate "mRS"
                               or "Dichotomous" model. Used to change
                               formatting in the app for model type.
    """
    # Pick bits out of the dataframe for all mRS:
    qalys_all_mrs = df['qalys_total'].to_list()
    total_discounted_cost_list = df['total_discounted_cost']

    # Get the results for just the selected mRS:
    results_dict = df.loc[mrs_input].to_dict()
    variables_dict = dict(**results_dict, **fixed_params)

    # Discounted total net benefit by change in outcome
    #     +---+---+---+---+---+---+
    #     | 0 | 1 | 2 | 3 | 4 | 5 |
    # +---+---+---+---+---+---+---+
    # | 0 |   |   |   |   |   |   |
    # | 1 |   |   |   |   |   |   |
    # | 2 |   |   |   |   |   |   |
    # | 3 |   |   |   |   |   |   |
    # | 4 |   |   |   |   |   |   |
    # | 5 |   |   |   |   |   |   |
    # +---+---+---+---+---+---+---+
    #
    st.markdown('### Discounted total Net Benefit by change in outcome')
    st.markdown(''.join([
        'Net Benefit is QALYs valued at Willingness to pay (WTP) ',
        'threshold, which is '
        f'£{variables_dict["wtp_qaly_gpb"]:.2f}, '
        'plus any cost savings.'
        ]))

    # Check which model we're using and draw a bespoke table:
    if model_input_str == 'mRS':
        write_example_cost_effectiveness(
            qalys_all_mrs,
            total_discounted_cost_list,
            variables_dict
            )
        write_table_cost_effectiveness(table_cost_effectiveness)
    else:
        write_table_cost_effectiveness_dicho(table_cost_effectiveness)


def write_table_cost_effectiveness(table_cost_effectiveness):
    """
    Write a table of the discounted resource use for each mRS.

    Use the non-removable index column as the mRS column. Don't label
    the columns so the default 0, 1, ... 5 can be mRS as well.
    Use the unicode characters to add empty space before a '-'
    to fake the right-alignment.

    Inputs:
    table_cost_effectiveness - 2D array. 6 rows by 6 columns.
                               Each cell contains the net cost benefit
                               for a change in outcome between
                               mRS=column value and mRS=row value.
    """
    # Use this function to colour values in the table:
    def color_negative_red(val):
        colour = None
        if len(val) > 0:
            if val[0] == '-' and val[-1] != '-':
                # Also check final character to check it's not a
                # string of one character, '-'.
                colour = 'red'
        return f'color: {colour}'

    # Change the table values to formatted strings:
    table = []
    for row in range(6):
        row_vals = []
        for column in range(6):
            diff_val = table_cost_effectiveness[row][column]
            if type(diff_val) == np.float64:
                # Either add a minus sign or a bit of empty space.
                sign = '-' if diff_val < 0 else '\U00002004'
                # Round pounds up (away from zero if -ve) to match Excel.
                # diff = sign+f'£{np.ceil(np.abs(diff_val)):.0f}'
                diff = sign+f'£{np.abs(diff_val):.0f}'
                # Add extra spaces at the start for right-alignment
                # cheat:
                extra_spaces = 10 - len(diff)
                diff = (
                    diff.split('£')[0] + '£' +
                    extra_spaces * '\U00002002' +
                    diff.split('£')[1]
                )
                row_vals.append(diff)
            elif column == row:
                # Show only a dash on the right-hand-side of the cell.
                row_vals.append(9*'\U00002002' + '-')
            else:
                row_vals.append('')
        table.append(row_vals)
    table = np.array(table)

    df_table = pd.DataFrame(table)

    # Write to streamlit:
    st.table(df_table.style.applymap(color_negative_red))
    st.caption(''.join([
        'Changes in outcome from column value to row value. ',
        'Numbers in red are increased costs to the NHS, ',
        'numbers in black represent savings to the NHS'
        ]))


def write_table_cost_effectiveness_dicho(table_cost_effectiveness):
    """
    Write a table of the discounted resource use for each mRS.

    This uses the first and final rows of the individual mRS table
    with re-labelled rows and column headings.
    Use the unicode characters to add empty space before a '-'
    to fake the right-alignment.

    Inputs:
    total_discounted_cost - array. List of the total discounted cost,
                            one value for each mRS.
    """
    # Use this function to colour values in the table:
    def color_negative_red(val):
        colour = None
        if len(val) > 0:
            if val[0] == '-' and val[-1] != '-':
                # Also check final character to check it's not a
                # string of one character, '-'.
                colour = 'red'
        return f'color: {colour}'

    diff_val = table_cost_effectiveness[-1, 0]
    # Either add a minus sign or a bit of empty space.
    sign = '-' if diff_val < 0 else '\U00002004'
    # Ready to delete (15th Dec 2022):
    # Round pounds up (away from zero if -ve) to match Excel.
    # diff = sign+f'£{np.ceil(np.abs(diff_val)):.0f}'
    diff = sign+f'£{np.abs(diff_val):.0f}'
    # Add extra spaces at the start for right-alignment
    # cheat:
    extra_spaces = 10 - len(diff)
    diff = (
        diff.split('£')[0] + '£' +
        extra_spaces * '\U00002002' +
        diff.split('£')[1]
    )

    table = [
        ['Independent', 9*'\U00002002' + '-', ''],
        ['Dependent', diff, 9*'\U00002002' + '-']
    ]
    table = np.array(table)

    df_table = pd.DataFrame(table, columns=['', 'Independent', 'Dependent'])

    # Write to streamlit:
    st.table(df_table.style.applymap(color_negative_red))
    st.caption(''.join([
        'Changes in outcome from column value to row value. ',
        'Numbers in red are increased costs to the NHS, ',
        'numbers in black represent savings to the NHS'
        ]))


def write_example_cost_effectiveness(
        qalys_all_mrs,
        total_discounted_cost_list,
        vd
        ):
    """
    Write example for calculating net benefit for change in outcome.

    Inputs:
    vd - dict. vd is short for variables_dict from main_calculations.
         It contains lots of useful constants and variables.
    """
    # Pick out some values for the example:
    qaly = qalys_all_mrs[1]-qalys_all_mrs[2]
    cost = total_discounted_cost_list[2]-total_discounted_cost_list[1]
    total = vd["wtp_qaly_gpb"]*qaly + cost

    # Write the example:
    st.markdown(''.join([
        'For example (where values in red change with the patient details) ',
        'the change from outcome mRS=1 to mRS=2 ',
        'has a discounted QALY of ',
        f'{qaly:.4f} ',
        'and a discounted total cost of ',
        f'£{cost:.0f}, ',
        'giving a net benefit of: '
    ]))
    st.latex(eqn.cost_effectiveness(vd, qaly, cost, total))
