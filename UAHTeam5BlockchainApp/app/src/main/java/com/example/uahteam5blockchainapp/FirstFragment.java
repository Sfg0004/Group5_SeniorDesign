package com.example.uahteam5blockchainapp;

import android.content.DialogInterface;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.RelativeLayout;
import android.widget.TextView;
import android.widget.Toast;
import android.Manifest;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AlertDialog;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;
import androidx.navigation.fragment.NavHostFragment;
import com.example.uahteam5blockchainapp.databinding.FragmentFirstBinding;

import java.io.File;

public class  FirstFragment extends Fragment
{
    private boolean LockDown;       //Variable to indicate if the blockchain is not verified. Thus, app is effectively disabled until it can be confirmed
    private FragmentFirstBinding binding;
    private PythonCode tempCaller;

    //Launcher to request permission to use the camera. If permission is granted, launch the camera launcher
    private ActivityResultLauncher<String[]> requestPermissionLauncher = registerForActivityResult(new ActivityResultContracts.RequestMultiplePermissions(), permissions ->
    {
        //If permission is granted to read and write files, do nothing
        if (permissions.getOrDefault(Manifest.permission.READ_EXTERNAL_STORAGE, false) && permissions.getOrDefault(Manifest.permission.WRITE_EXTERNAL_STORAGE, false)) {
            //Toast.makeText(getContext(), "Permission granted to read and write to files", Toast.LENGTH_SHORT).show();
        }
    });

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState)
    {
        binding = FragmentFirstBinding.inflate(inflater, container, false);
        String[] requiredPermissions1 = {Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE};
        //Calls the python code object
        tempCaller = PythonCode.PythonCode(getContext());
        requestPermissionLauncher.launch(requiredPermissions1);      //Launch the permission launcher to get the needed permissions
        return binding.getRoot();
    }

    public void onViewCreated(View view, Bundle savedInstanceState)
    {
        super.onViewCreated(view, savedInstanceState);
        //Checks if the SavedImages directory exists. If not, create it
        File SavedImagesDirectory = new File(requireContext().getExternalFilesDir(null) + "/SavedImages");
        //If the directory does not exist, create it
        if (!SavedImagesDirectory.exists())
        {
            //Create the directory, and processes the result
            //Should never happen
            if (!SavedImagesDirectory.mkdirs())
            {
                Toast.makeText(requireContext(), "Cannot save images to upload", Toast.LENGTH_SHORT).show();        //Informs the user of the error
                Log.e("Directory doesn't exist", "The directory SavedImages does not exist and could not be created.");     //Logs the error
            }
        }
        //Checks if the SavedImages directory exists. If not, create it
        File DownloadedFilesDirectory = new File(requireContext().getExternalFilesDir(null) + "/DownloadedFiles");
        //If the directory does not exist, create it
        if (!DownloadedFilesDirectory.exists())
        {
            //Create the directory, and processes the result
            //Should never happen
            if (!DownloadedFilesDirectory.mkdirs())
            {
                Toast.makeText(requireContext(), "Cannot save downloaded files", Toast.LENGTH_SHORT).show();        //Informs the user of the error
                Log.e("Directory doesn't exist", "The directory DownloadedFiles does not exist and could not be created.");     //Logs the error
            }
        }
        //Checks if the data directory exists. If not, create it
        File DataDirectory = new File(requireContext().getExternalFilesDir(null) + "/data");
        //If the directory does not exist, create it
        if (!DataDirectory.exists())
        {
            //Create the directory, and processes the result
            //Should never happen
            if (!DataDirectory.mkdirs())
            {
                Toast.makeText(requireContext(), "Cannot create directory to save data", Toast.LENGTH_SHORT).show();        //Informs the user of the error
                Log.e("Directory doesn't exist", "The directory data does not exist and could not be created.");     //Logs the error
            }
        }

        //Sets the listener for the logout button
        //Independent of the lockdown mechanism flag
        binding.buttonLogout.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
                //Creates an alert dialog to show that
                AlertDialog.Builder builder = new AlertDialog.Builder(requireContext());
                builder.setTitle("Confirm Logout");
                builder.setMessage("Are you sure you want to logout?");
                //Creates two buttons
                //Creates the button to for the positive action
                builder.setPositiveButton("Yes", new DialogInterface.OnClickListener()
                {
                    public void onClick(DialogInterface logoutDialog, int ID)
                    {
                        //Mark the user as logged out
                        tempCaller.setLoggedIn(false);
                        //Erase the needed files

                        //Navigate back to the login Fragment
                        returnToLoginFragment();
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

        //Check validity of the blockchain
        //LockDown = getValidity();
        //Until this is implemented, lockdown will be false
        LockDown = false;
        //If lockdown mode is not valid, prevent the app from working
        if (LockDown)
        {
            //Create an image with an x-mark on it to show the blockchain is invalid
            RelativeLayout statusLayout = view.findViewById(R.id.statusLayout);
            ImageView BlockchainStatusIcon = view.findViewById(R.id.BlockchainStatusIcon);
            TextView BlockchainStatusTextView = view.findViewById(R.id.BlockchainStatusTextView);

            //Shows the image to indicate a failure in the blockchain
            BlockchainStatusIcon.setImageResource(R.drawable.failuremark);
            BlockchainStatusTextView.setText(getString(R.string.IBInstructions));
            statusLayout.setVisibility(View.VISIBLE);           //Makes the images visible

            //Displays a Toast message saying the blockchain is invalid, so advice reloading the app
            Toast.makeText(getContext(), R.string.IBInstructions, Toast.LENGTH_LONG).show();


            //Sets the listener for the files button
            binding.buttonFiles.setOnClickListener(new View.OnClickListener() {
               @Override
               public void onClick(View view) {
                   Toast.makeText(getContext(), R.string.IBInstructions, Toast.LENGTH_LONG).show();
               }
            });
            //Sets the listener for the download button
            binding.buttonDownload.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    Toast.makeText(getContext(), R.string.IBInstructions, Toast.LENGTH_LONG).show();
                }
            });
            //Sets the listener for the upload button
            binding.buttonUpload.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    Toast.makeText(getContext(), R.string.IBInstructions, Toast.LENGTH_LONG).show();
                }
            });

        }
        //Else, blockchain is valid
        else
        {
            //Create an image with an x-mark on it to show the blockchain is invalid
            RelativeLayout statusLayout = view.findViewById(R.id.statusLayout);
            ImageView BlockchainStatusIcon = view.findViewById(R.id.BlockchainStatusIcon);
            TextView BlockchainStatusTextView = view.findViewById(R.id.BlockchainStatusTextView);

            //Shows the image to indicate a failure in the blockchain
            BlockchainStatusIcon.setImageResource(R.drawable.checkmark);
            BlockchainStatusTextView.setText(getString(R.string.validBlockchain));
            statusLayout.setVisibility(View.VISIBLE);           //Makes the images visible
            //Checks if permission to read/write to the files is granted. If not, requests them
            if (!RWPermissionGranted())
            {
                //Requests permission to read/write to files
                //Creates a List of the permissions required to run the app
                String[] requiredPermissions = {Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE};
                requestPermissionLauncher.launch(requiredPermissions);      //Launch the permission launcher to get the needed permissions
            }
            //Sets the listener for the button and for the resulting action when the button is pressed
            binding.buttonUpload.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    //If the app is  locked down, then make the button press invoke a Toast message
                    if (LockDown)
                    {
                        Toast.makeText(getContext(), R.string.IBInstructions, Toast.LENGTH_LONG).show();
                    }
                    //Else, the app is open to use
                    else
                    {
                        //Checks if permission to read/write to the files is granted. If not, requests them
                        if (!RWPermissionGranted()) {
                            //Informs the user that permission is needed to use the app
                            Toast.makeText(getContext(), "App requires files access\npermissions to work", Toast.LENGTH_LONG).show();
                            //Requests permission to read/write to files
                            //Creates a List of the permissions required to run the app
                            String[] requiredPermissions1 = {Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE};
                            requestPermissionLauncher.launch(requiredPermissions1);      //Launch the permission launcher to get the needed permissions
                        }
                        else
                        {
                            //Redirects the fragment from the First Fragment to the Upload Fragment
                            NavHostFragment.findNavController(FirstFragment.this).navigate(R.id.action_FirstFragment_to_UploadFragment);
                        }
                    }
                }
            });

            //Sets the listener for the button and for the resulting action when the button is pressed
            binding.buttonDownload.setOnClickListener(new View.OnClickListener()
            {
                @Override
                public void onClick(View view) {
                    //If the app is  locked down, then make the button press invoke a Toast message
                    if (LockDown)
                    {
                        Toast.makeText(getContext(), R.string.IBInstructions, Toast.LENGTH_LONG).show();
                    }
                    //Else, the app is open to use
                    else
                    {
                        //Checks if permission to read/write to the files is granted. If not, requests them
                        if (!RWPermissionGranted())
                        {
                            //Informs the user that permission is needed to use the app
                            Toast.makeText(getContext(), "App requires files access\npermissions to work", Toast.LENGTH_LONG).show();
                            //Requests permission to read/write to files
                            //Creates a List of the permissions required to run the app
                            String[] requiredPermissions2 = {Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE};
                            requestPermissionLauncher.launch(requiredPermissions2);      //Launch the permission launcher to get the needed permissions
                        }
                        else
                        {
                            //Redirects the fragment from the First Fragment to the Download Fragment
                            NavHostFragment.findNavController(FirstFragment.this).navigate(R.id.action_FirstFragment_to_DownloadFragment);
                        }
                    }
                }
            });


            //Sets the listener for the button and for the resulting action when the button is pressed
            binding.buttonFiles.setOnClickListener(new View.OnClickListener()
            {
                @Override
                public void onClick(View view)
                {
                    //If the app is  locked down, then make the button press invoke a Toast message
                    if (LockDown)
                    {
                        Toast.makeText(getContext(), R.string.IBInstructions, Toast.LENGTH_LONG).show();
                    }
                    //Else, the app is open to use
                    else
                    {
                        //Checks if permission to read/write to the files is granted. If not, requests them
                        if (!RWPermissionGranted())
                        {
                            //Informs the user that permission is needed to use the app
                            Toast.makeText(getContext(), "App requires files access\npermissions to work", Toast.LENGTH_LONG).show();
                            //Requests permission to read/write to files
                            //Creates a List of the permissions required to run the app
                            String[] requiredPermissions3 = {Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE};
                            requestPermissionLauncher.launch(requiredPermissions3);      //Launch the permission launcher to get the needed permissions
                        }
                        else
                        {
                            //Redirects the fragment from the First Fragment to the Download Fragment
                            NavHostFragment.findNavController(FirstFragment.this).navigate(R.id.action_FirstFragment_to_FilesFragment);
                        }
                    }
                }
            });
        }
    }

    //Function to check if read/write permission has been granted for files
    //Returns true if granted, and false if denied
    private boolean RWPermissionGranted()
    {
        //If permission is not granted, then the app will not run
        //Checks if permission is denied
        if ((ContextCompat.checkSelfPermission(requireContext(), Manifest.permission.READ_EXTERNAL_STORAGE) == PackageManager.PERMISSION_DENIED) && (ContextCompat.checkSelfPermission(requireContext(), Manifest.permission.WRITE_EXTERNAL_STORAGE) == PackageManager.PERMISSION_DENIED))
        {
            Log.e("permission denied", "cannot write to external media");
            return false;               //Returns false to show that the permission has been denied
        }
        //Else, permission is granted
        else
        {
            return true;               //Returns false to show that the permission has been granted
        }
    }

    //Function to return control back to the login fragment
    private void returnToLoginFragment()
    {
        //Inform the user that the logout was successful
        Toast.makeText(requireContext(), "Logout Successful", Toast.LENGTH_SHORT).show();
        //Navigates back to the login Fragment
        NavController navController = Navigation.findNavController(requireActivity(), R.id.nav_host_fragment_content_main);
        navController.popBackStack(navController.getGraph().getStartDestinationId(), false);
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }
}

//old code
/*

    //
    //
    //
    //Need to make sure the first fragment, when it requests permissions, does not lock down the controls, especially for accessing external media
    //
    //
    //
    private Spinner roleSpinner;

mo
        //Initializes the spinner for the dropdown
        roleSpinner = requireView().findViewById(R.id.roleDropdown);
        //Defines the list of possible options to choose from
        String[] possibleRoles = {"Doctor", "Patient", "Admin"};
        //Creates an ArrayAdapter to contain the list of potential roles
        ArrayAdapter<String> dropdownAdapter = new ArrayAdapter<>(requireContext(), android.R.layout.simple_spinner_dropdown_item, possibleRoles);
        //Sets the dropdown resource to a spinner dropdown
        dropdownAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        //Connects the adapter to the Spinner
        roleSpinner.setAdapter(dropdownAdapter);
        //Makes the default selection "Doctor"
        roleSpinner.setSelection(0, false);


     */
