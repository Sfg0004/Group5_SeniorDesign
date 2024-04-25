package com.example.uahteam5blockchainapp;

import android.content.DialogInterface;
import android.os.Bundle;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Spinner;
import android.widget.ArrayAdapter;
import androidx.appcompat.app.AlertDialog;
import androidx.fragment.app.Fragment;
import androidx.navigation.fragment.NavHostFragment;
import com.example.uahteam5blockchainapp.databinding.FragmentCreateUserBinding;

public class CreateUserFragment extends Fragment
{
    private Spinner roleSpinner;        //Creates a spinner to handle the roles
    private FragmentCreateUserBinding binding;
    private PythonCode tempCaller;      //Python code caller to interact with the blockchain

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState)
    {
        binding = FragmentCreateUserBinding.inflate(inflater, container, false);
        //Creates the PythonCode object to interact with the blockchain
        tempCaller = PythonCode.PythonCode(getContext());
        return binding.getRoot();
    }

    public void onViewCreated(View view, Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        //Makes the text input boxes centered
        binding.editFullName.setGravity(Gravity.CENTER);
        binding.editUsername.setGravity(Gravity.CENTER);
        binding.editPassword.setGravity(Gravity.CENTER);
        binding.editConfirmPassword.setGravity(Gravity.CENTER);
        //Initializes the spinner for the dropdown
        roleSpinner = requireView().findViewById(R.id.roleDropdown);
        //Defines the list of possible options to choose from
        String[] possibleRoles = {"Patient", "Doctor", "Admin"};
        //Creates an ArrayAdapter to contain the list of potential roles
        ArrayAdapter<String> dropdownAdapter = new ArrayAdapter<>(requireContext(), android.R.layout.simple_spinner_dropdown_item, possibleRoles);
        //Sets the dropdown resource to a spinner dropdown
        dropdownAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        //Connects the adapter to the Spinner
        roleSpinner.setAdapter(dropdownAdapter);
        //Makes the default selection "Patient"
        roleSpinner.setSelection(0, false);

        //Gets the selected role as a String from the role box
        String chosenRole = roleSpinner.getSelectedItem().toString();

        //Sets a listener for the cancel creation button
        binding.CancelCreation.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
                //Creates an alert dialog to show that
                AlertDialog.Builder builder = new AlertDialog.Builder(requireContext());
                builder.setTitle("Confirm Cancel");
                builder.setMessage("Are you sure you want cancel?");
                //Creates two buttons
                //Creates the button to for the positive action
                builder.setPositiveButton("Yes", new DialogInterface.OnClickListener()
                {
                    public void onClick(DialogInterface logoutDialog, int ID)
                    {
                        //Clears the text boxes
                        binding.editFullName.setText("");
                        binding.editUsername.setText("");
                        binding.editPassword.setText("");
                        binding.editConfirmPassword.setText("");
                        //Makes the default selection "Patient"
                        roleSpinner.setSelection(0, false);
                        //Navigate back to the admin Fragment
                        NavHostFragment.findNavController(CreateUserFragment.this).navigate(R.id.action_CreateUserFragment_to_AdminFragment);
                    }
                });
                //Creates the button to for the positive action
                builder.setNegativeButton("No", new DialogInterface.OnClickListener()
                {
                    public void onClick(DialogInterface logoutDialog, int ID)
                    {
                        //Do nothing, but dismisses the dialog box
                        logoutDialog.dismiss();
                    }
                });
                //Creates the dialog box
                AlertDialog logoutDialog = builder.create();
                //Shows the dialog box
                logoutDialog.show();
            }
        });

        //Sets a listener for the confirm creation button
        binding.ConfirmCreation.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
                ///Checks to make sure all boxes are filled
                if (!binding.editFullName.getText().toString().isEmpty() && !binding.editPassword.getText().toString().isEmpty() && !binding.editConfirmPassword.getText().toString().isEmpty() && !binding.editUsername.getText().toString().isEmpty()) {
                    //If the passwords match
                    if ((binding.editPassword.getText().toString().equals(binding.editConfirmPassword.getText().toString())))
                    {
                        //Creates an alert dialog to show that
                        AlertDialog.Builder builder = new AlertDialog.Builder(requireContext());
                        //Sets the title for the dialog box
                        builder.setTitle("Confirm User Creation");
                        //Sets the message for the dialog box
                        builder.setMessage("Are you sure you want create this account?");
                        //Creates two buttons
                        //Creates the button to for the positive action
                        builder.setPositiveButton("Yes", new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface logoutDialog, int ID) {
                                //Dismisses the dialog box
                                logoutDialog.dismiss();
                                //Updates the local blockchain first
                                tempCaller.refreshBlockchain();
                                //Creates a temp variable for the role of the user
                                //Should not have an issue with role selection


                                //Commented out to handle the python code
                                //If this gets uncommented, replace "roleSpinner.getSelectedItem().toString()", with 'role'
                                /*
                                String role;
                                //Switches to convert the role into a string
                                switch (roleSpinner.getSelectedItem().toString()) {
                                    case "Admin":
                                        role = "a";
                                        break;
                                    case "Doctor":
                                        role = "d";
                                        break;
                                    //By default, user account is a patient
                                    default:
                                        role = "p";
                                        break;
                                }*/


                                //Gets the information from the input boxes and makes the user account using the given information
                                boolean accountCreatedOrNot = tempCaller.createUser(binding.editFullName.getText().toString(), binding.editUsername.getText().toString(), binding.editPassword.getText().toString(), roleSpinner.getSelectedItem().toString());        //Calls the Python code the download the file
                                //Create a dialog box showing the status of account creation
                                AlertDialog.Builder userCreated = new AlertDialog.Builder(requireContext());
                                //Sets the button for the dialog box
                                userCreated.setPositiveButton("Ok", new DialogInterface.OnClickListener() {
                                    public void onClick(DialogInterface logoutDialog, int ID)
                                    {
                                        //Clears the text boxes
                                        binding.editFullName.setText("");
                                        binding.editUsername.setText("");
                                        binding.editPassword.setText("");
                                        binding.editConfirmPassword.setText("");
                                        //Makes the default selection "Patient"
                                        roleSpinner.setSelection(0, false);
                                        //Dismisses the dialog box
                                        logoutDialog.dismiss();
                                        //If the account was created successfully, move back to the admin fragment when "ok" is pressed
                                        if (accountCreatedOrNot)
                                        {
                                            //Navigate back to the admin Fragment
                                            NavHostFragment.findNavController(CreateUserFragment.this).navigate(R.id.action_CreateUserFragment_to_AdminFragment);
                                        }
                                    }
                                });
                                //If the account was created successfully
                                if (accountCreatedOrNot) {
                                    //Sets the text for the dialog box
                                    userCreated.setTitle("Account Created Successfully");
                                }
                                //Else, the account was not created successfully
                                else {
                                    //Sets the text for the dialog box
                                    userCreated.setTitle("Account Creation Failed");
                                    userCreated.setMessage("Account with that username already exists");
                                }
                                //Creates the dialog box
                                AlertDialog userManufactured = userCreated.create();
                                //Shows the dialog box
                                userManufactured.show();
                            }
                        });
                        //Creates the button to for the positive action
                        builder.setNegativeButton("No", new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface logoutDialog, int ID) {
                                //Do nothing, but dismisses the dialog box
                                logoutDialog.dismiss();
                            }
                        });
                        //Creates the dialog box
                        AlertDialog logoutDialog = builder.create();
                        //Shows the dialog box
                        logoutDialog.show();
                    }
                    //Else, the passwords do not match, so process
                    else
                    {
                        //Create a dialog box showing the status of account creation
                        AlertDialog.Builder passwordError = new AlertDialog.Builder(requireContext());
                        //Sets the button for the dialog box
                        passwordError.setPositiveButton("Ok", new DialogInterface.OnClickListener()
                        {
                            public void onClick(DialogInterface logoutDialog, int ID)
                            {
                                //Dismisses the dialog box
                                logoutDialog.dismiss();
                            }
                        });
                        //Sets the text for the dialog box
                        passwordError.setMessage("Passwords do not match");
                        //Creates the dialog box
                        AlertDialog passwordAlert = passwordError.create();
                        //Shows the dialog box
                        passwordAlert.show();
                    }
                }
                //Else, bad input was provided, so alert and process as such
                else
                {
                    //Create a dialog box showing the status of account creation
                    AlertDialog.Builder inputError = new AlertDialog.Builder(requireContext());
                    //Sets the button for the dialog box
                    inputError.setPositiveButton("Ok", new DialogInterface.OnClickListener()
                    {
                        public void onClick(DialogInterface logoutDialog, int ID)
                        {
                            //Dismisses the dialog box
                            logoutDialog.dismiss();
                        }
                    });
                    //Sets the text for the dialog box
                    inputError.setTitle("Account Creation Error");
                    //Note, need to set to.equals("")
                    String errorMessage = "The following fields must be filled:\n\n";

                    //If the all boxes are empty, notify the user of such
                    if (binding.editFullName.getText().toString().isEmpty())
                    {
                        //Adds to the message for the dialog box
                        errorMessage += "Full Name\n";
                    }
                    //Else, if the username name was not inputted
                    if (binding.editUsername.getText().toString().isEmpty())
                    {
                        //Adds to the message for the dialog box
                        errorMessage += "Username\n";
                    }
                    //Else, if the password field was not filled
                    if (binding.editPassword.getText().toString().isEmpty())
                    {
                        //Adds to the message for the dialog box
                        errorMessage += "Password\n";
                    }
                    //Else, if the confirm password field was not filled
                    if (binding.editConfirmPassword.getText().toString().isEmpty())
                    {
                        //Adds to the message for the dialog box
                        errorMessage += "Confirm Password\n";
                    }
                    //Sets the error message for the alert box
                    inputError.setMessage(errorMessage);
                    //Creates the dialog box
                    AlertDialog errorAlert = inputError.create();
                    //Shows the dialog box
                    errorAlert.show();
                }
            }
        });
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }
}
