 package com.example.uahteam5blockchainapp;

import android.Manifest;
import android.content.DialogInterface;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.os.Environment;
import android.text.InputType;
import android.util.Log;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AlertDialog;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;
import androidx.navigation.fragment.NavHostFragment;
import android.view.animation.AlphaAnimation;
import android.view.animation.Animation;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.FileWriter;
import java.util.Objects;
import java.util.Scanner;
import java.io.File;

import com.example.uahteam5blockchainapp.databinding.FragmentLoginBinding;

 public class LoginFragment extends Fragment
{
    private boolean requireLogin;       //Variable that shows if the user needs to login
    private FragmentLoginBinding binding;
    private PythonCode tempCaller;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState)
    {
        binding = FragmentLoginBinding.inflate(inflater, container, false);
        return binding.getRoot();
    }

    @Override
    public void onViewCreated(View view, Bundle savedInstanceState)
    {
        super.onViewCreated(view, savedInstanceState);
        //Centers the username and password text boxes
        binding.editUsername.setGravity(Gravity.CENTER);
        //Calls the python code object
        tempCaller = PythonCode.PythonCode(getContext());
        binding.editTextPassword.setGravity(Gravity.CENTER);
        //First, check if the file exists that contains the IP
        File destinationIP = new File(getContext().getFilesDir().toString() + "/targetIP.txt");


        //Uncomment this to verify the IP is correct
        //destinationIP.delete();


        //Gets the first line from the file
        String firstLine = getFirstLineFromFile(getContext().getFilesDir().toString() + "/targetIP.txt");
        //Based on the checks from getFirstLineFromFile(), the file either exists, or there in bad data in the file/the file doesn't exist
        //If the tests failed
        if (firstLine == null)
        {
            //Tries to create a new file and write an IP to it
            try
            {
                //Creates the new file
                destinationIP.createNewFile();
                //Creates a new dialog box to get the user's inputted target IP
                getValidIP();
            }
            //While this should not happen, handle if there is an error
            catch (IOException error)
            {
                //Logs the error
                Log.e("Manual termination", "Terminated for failing to create '" + Environment.getExternalStorageDirectory() + "/targetIP.txt'");
                getActivity().finish();     //Terminates the app
            }
        }
        //Checks if the data directory exists
        File currentDirectory = new File(Environment.getExternalStorageDirectory() + "/data");
        //If the directory does not exist
        if (!currentDirectory.exists())
        {
            //Makes the directory
            new File(Environment.getExternalStorageDirectory() + "/data").mkdir();
            //Requires a user to login
            requireLogin = true;
        }
        //Else, the directory exists
        else
        {
            //Check if the data file exists
            File currentLogin = new File(Environment.getExternalStorageDirectory() + "/data/current.txt");
            if (currentLogin.exists())
            {
                //Opens and processes the file looking for the current login
                try
                {
                    //Creates a new scanner to look in the file for the current login information
                    Scanner loginReader = new Scanner(currentLogin);
                    //Gets the first line of the file that holds the username, password hash, and blockchainID
                    String username = loginReader.nextLine();
                    String passwordHash = loginReader.nextLine();
                    String blockchainID = loginReader.nextLine();
                    //Now, compares those values against the login file
                    //If the login credentials are found in the file, then don't require the user to login
                    if (searchLoginFile(username, passwordHash, blockchainID))
                    {
                        requireLogin = false;
                    }
                    //Else, the user is not logged in, so require a login
                    else
                    {
                        requireLogin = true;
                    }
                }
                //This should never happen, but left in to keep Java happy
                catch (FileNotFoundException e)
                {
                    throw new RuntimeException(e);
                }
            }
            //Else, the login file does not exist
            else
            {
                //Requires the user to login
                requireLogin = true;
                //Creates the login file
                try
                {
                    new File(Environment.getExternalStorageDirectory() + "/data/logs.txt").createNewFile();
                }
                //Should not happen, but done to make Java happy
                catch (IOException e)
                {
                    throw new RuntimeException(e);
                }
            }
        }//default format should be      username:salt:passwordHash

        //Makes the incorrect password text animate its disappearance
        TextView incorrectPassword = view.findViewById(R.id.incorrectPassword);
        AlphaAnimation fadeOut = new AlphaAnimation(1.0f, 0.0f);        //Sets the range of fading
        //Creates a new animation from 100% to 100% visibility so the user will see it
        AlphaAnimation stayUp = new AlphaAnimation(1.0f, 1.0f);
        //Sets the duration to 5s
        stayUp.setDuration(5000);
        //Keeps its state after the animation ends
        stayUp.setFillAfter(true);
        fadeOut.setDuration(20000);     //Sets the fade out duration to 20000ms = 20s
        //Defines what happens in the different stages of the animation
        fadeOut.setAnimationListener(new Animation.AnimationListener() {
            @Override
            public void onAnimationStart(Animation animation)
            {

            }

            @Override
            public void onAnimationEnd(Animation animation)
            {
                incorrectPassword.setVisibility(View.INVISIBLE);        //Makes the incorrect password box invisible after fading
            }

            @Override
            public void onAnimationRepeat(Animation animation) {

            }
        });

        //Defines what happens in the different stages of the animation
        stayUp.setAnimationListener(new Animation.AnimationListener() {
            @Override
            public void onAnimationStart(Animation animation)
            {
                //Makes the red text visible
                incorrectPassword.setVisibility(View.VISIBLE);
            }

            @Override
            public void onAnimationEnd(Animation animation)
            {
                //When the animation ends, start the fade out animation
                incorrectPassword.startAnimation(fadeOut);
            }

            @Override
            public void onAnimationRepeat(Animation animation)
            {
                //Starts the face out animation
                incorrectPassword.startAnimation(fadeOut);
            }
        });

        //Sets the listener for the login button
        binding.buttonLogin.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
                //Gets the username from the input box
                String username = binding.editUsername.getText().toString();
                //Gets the password from the input box
                String password = binding.editTextPassword.getText().toString();
                //Gets the result of the login
                boolean status = tempCaller.login(username, password);
                //Toast.makeText(getContext(), Boolean.toString(status), Toast.LENGTH_LONG).show();
                //Navigates to the first fragment
                //NavHostFragment.findNavController(LoginFragment.this).navigate(R.id.action_LoginFragment_to_FirstFragment);
                //NavHostFragment.findNavController(LoginFragment.this).navigate(R.id.action_LoginFragment_to_AdminFragment);



                //If the login was successful
                if (status == true)
                {
                    //Clears the username and password text boxes
                    binding.editUsername.setText("");
                    //Clears the password text input box
                    binding.editTextPassword.setText("");
                    //Get the account information from the python code



                    //Gets the status of the switch and checks if the user has selected the stay logged in switch
                    if (binding.stayLoggedInSwitch.isChecked())
                    {
                        //Saves the information into the current.txt file

                    }
                    //Gets the role of the user
                    String userRole = tempCaller.getUserRole(username);
                    //Else, the user has not, so empty the login credentials file
                    //Based on the role of the user, login as such
                    if (userRole.equals("a"))
                    {
                        //Navigates to the admin fragment
                        NavHostFragment.findNavController(LoginFragment.this).navigate(R.id.action_LoginFragment_to_AdminFragment);
                    }
                    //Else, the user is a patient or a doctor, so move to the default view
                    else
                    {
                        //Navigates to the default fragment
                        NavHostFragment.findNavController(LoginFragment.this).navigate(R.id.action_LoginFragment_to_FirstFragment);
                    }
                }
                //Else, the login failed, so inform the user
                else
                {
                    //If both fields are empty, inform the user
                    if (username.isEmpty() && password.isEmpty())
                    {
                        incorrectPassword.setText("Username and password required");
                    }
                    //If the username is empty, inform the user
                    else if (username.isEmpty())
                    {
                        incorrectPassword.setText("Username required");
                    }
                    //If the password is empty, inform the user
                    else if (password.isEmpty())
                    {
                        incorrectPassword.setText("Password required");
                    }
                    //Else, the password is invalid, so inform the user
                    else
                    {
                        //Clears the password text input box
                        binding.editTextPassword.setText("");
                        incorrectPassword.setText("Invalid Login");
                    }
                    //Starts the incorrect password animation
                    incorrectPassword.startAnimation(stayUp);
                }
            }
        });

        //If login is not required
        if (!requireLogin)
        {
            //Navigate to the next fragment, the first fragment
            //NavHostFragment.findNavController(LoginFragment.this).navigate(R.id.action_LoginFragment_to_FirstFragment);
        }
        //Else, the user has to login
        else
        {

        }
    }

    //Function to ensure a valid IP is obtained
    private void getValidIP()
    {
        //Creates an alert dialog to inform the user
        AlertDialog.Builder builder = new AlertDialog.Builder(getContext());
        builder.setTitle("Input target IP");
        //Creates a mew edit text box to get data from the user
        EditText inputText = new EditText(getContext());
        //Gets numbers and dots from the user
        inputText.setInputType(InputType.TYPE_CLASS_PHONE);
        //Links the builder to the edit text box
        builder.setView(inputText);
        //Creates the button to for the acknowledgement action
        builder.setPositiveButton("Ok", new DialogInterface.OnClickListener()
        {
            public void onClick(DialogInterface IPPromptDialog, int ID)
            {
                //If the IP is valid, dismiss the box and write the data to the data file
                if (validateIP(inputText.getText().toString()))
                {
                    //Dismisses the logout dialog box
                    IPPromptDialog.dismiss();
                    try
                    {
                        //Creates a new file writer to write to the file
                        FileWriter fileWriter = new FileWriter(getContext().getFilesDir().toString() + "/targetIP.txt");
                        //Writes the IP to the file
                        fileWriter.write(inputText.getText().toString());
                        //Closes the file writer
                        fileWriter.close();
                    }
                    //While this should not happen, handle if there is an error
                    catch (IOException error)
                    {
                        //Logs the error
                        Log.e("Manual termination", "Terminated for failing to open '" + getContext().getFilesDir().toString() + "/targetIP.txt'");
                        getActivity().finish();     //Terminates the app
                    }
                }
            }
        });
        //Creates a new listener for when the display is displayed
        builder.setOnDismissListener(new DialogInterface.OnDismissListener() {
            @Override
            public void onDismiss(DialogInterface dialog)
            {
                //If an invalid IP
                if (!validateIP(inputText.getText().toString()))
                {
                    //Creates a toast message to inform the user that the IP is not formatted correctly
                    Toast.makeText(getContext(), "Invalid IP address format. Try again.", Toast.LENGTH_LONG).show();
                    //Calls the function to get a valid IP
                    getValidIP();
                }
            }
        });
        //Creates the dialog box
        AlertDialog IPPromptDialog = builder.create();
        //Shows the dialog box
        IPPromptDialog.show();
    }

    //Function to search the login file for the information
    private boolean searchLoginFile(String username, String passwordHash, String blockchainID)
    {
        //Else, the login credentials were not found in the input file, so return false to show that the login info was not found
        return false;
    }

    //Function to validate the IP. Borrowed from "https://stackoverflow.com/questions/5667371/validate-ipv4-address-in-java"
    public static boolean validateIP(final String ip) {
        String PATTERN = "^((0|1\\d?\\d?|2[0-4]?\\d?|25[0-5]?|[3-9]\\d?)\\.){3}(0|1\\d?\\d?|2[0-4]?\\d?|25[0-5]?|[3-9]\\d?)$";

        return ip.matches(PATTERN);
    }

    //Function to get the first line from the given file
    private String getFirstLineFromFile(String filePath)
    {
        //Creates a new file handler for the file
        File newFile = new File(filePath);
        //Ensures the file exists
        if (newFile.exists())
        {
            //Tries to read from the file
            try
            {
                //Opens the file and reads the first line
                Scanner newScanner = new Scanner(newFile);
                //Gets the first line of text
                String resultingData = newScanner.nextLine();
                //If the IP is validated
                if (validateIP(resultingData))
                {
                    //Returns the correct IP
                    return resultingData;
                }
                //Else, the IP is invalidated, so return null
                return null;
            }
            //This should not happen as the file has ben confirmed to exist
            catch (FileNotFoundException error)
            {
                //Logs the error
                Log.e("Manual termination", "Terminated for an impossible condition happening");
                getActivity().finish();     //Terminates the app
            }

        }
        //Else, file does not exist so terminate
        return null;
    }

    @Override
    public void onDestroyView()
    {
        super.onDestroyView();
        binding = null;
    }
}

/*
//Extra code to animate an image
ImageView blockchainLogo = view.findViewById(R.id.logoView);       //Gets the image view
AlphaAnimation fadeIn = new AlphaAnimation(0.0f, 1.0f);     //Fades in
fadeIn.setDuration(3000);       //Sets the fade in to 3000 ms = 3s
blockchainLogo.startAnimation(fadeIn);      //Starts the animation
*/