package com.example.uahteam5blockchainapp;

import android.content.DialogInterface;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Toast;
import androidx.appcompat.app.AlertDialog;
import androidx.fragment.app.Fragment;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;
import androidx.navigation.fragment.NavHostFragment;
import com.example.uahteam5blockchainapp.databinding.FragmentAdminBinding;
import java.util.ArrayList;

public class AdminFragment extends Fragment
{
    private FragmentAdminBinding binding;
    private PythonCode tempCaller;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState)
    {
        binding = FragmentAdminBinding.inflate(inflater, container, false);
        return binding.getRoot();
    }

    public void onViewCreated(View view, Bundle savedInstanceState)
    {
        super.onViewCreated(view, savedInstanceState);
        //Initializes the python code caller for the fragment
        tempCaller = PythonCode.PythonCode(getContext());
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

        //Sets the listener for the create user button
        binding.CreateUser.setOnClickListener(new View.OnClickListener()
        {
            @Override
            public void onClick(View view)
            {
                //Navigates to the Create User fragment
                NavHostFragment.findNavController(AdminFragment.this).navigate(R.id.action_AdminFragment_to_CreateUserFragment);
            }
        });

        //Sets the listener for the view blockchain button
        binding.ViewBlockchain.setOnClickListener(new View.OnClickListener()
        {
            @Override
            public void onClick(View view)
            {
                //Creates the next fragment variable
                ViewDataFragment newFragment = new ViewDataFragment();
                //Declares a new bundle to handle the string being sent to the next fragment
                Bundle stringBundle = new Bundle();
                //Updates the local blockchain first
                tempCaller.refreshBlockchain();
                //Calls the function to get the list of active users
                String currentBlockchain = tempCaller.getCurrentBlockchain();
                //Adds the string to the bundle
                stringBundle.putString("textToDisplay", currentBlockchain);
                //Adds the string for the title to the bundle
                stringBundle.putString("title", "Blockchain");
                //Sends the arguments to the next fragment
                newFragment.setArguments(stringBundle);
                //Navigates to the ViewData fragment
                NavHostFragment.findNavController(AdminFragment.this).navigate(R.id.action_AdminFragment_to_ViewDataFragment, stringBundle);
            }
        });

        //Sets the listener for the view active users button
        binding.viewActiveUsers.setOnClickListener(new View.OnClickListener()
        {
            @Override
            public void onClick(View view)
            {
                //Creates the next fragment variable
                ViewDataFragment newFragment = new ViewDataFragment();
                //Declares a new bundle to handle the string being sent to the next fragment
                Bundle stringBundle = new Bundle();
                //String variable to hold the string being passed onto the next fragment
                String tempData = "\n";
                //Updates the local blockchain first
                tempCaller.refreshBlockchain();
                //Calls the function to get the list of active users
                ArrayList<String> activeUsers = tempCaller.getListActiveUsers();
                //Processes the active users and creates a list of their user names
                for (int i = 0; i < activeUsers.size(); i++)
                {
                    tempData += (activeUsers.get(i) + "\n");
                }
                //Adds the string to the bundle
                stringBundle.putString("textToDisplay", tempData);
                //Adds the string for the title to the bundle
                stringBundle.putString("title", "Active Users");
                //Sends the arguments to the next fragment
                newFragment.setArguments(stringBundle);
                //Navigates to the ViewData fragment
                NavHostFragment.findNavController(AdminFragment.this).navigate(R.id.action_AdminFragment_to_ViewDataFragment, stringBundle);
            }
        });

        //Check validity of the blockchain
        //LockDown = getValidity();
        //Until this is implemented, lockdown will be true
        boolean LockDown = true;


    }

    //Function to return control back to the login fragment
    private void returnToLoginFragment()
    {
        //Inform the user that the logout was successful
        Toast.makeText(requireContext(), "Logout Successful", Toast.LENGTH_SHORT).show();
        //Goes back to the Login fragment
        //Navigates back to the login Fragment
        NavController navController = Navigation.findNavController(requireActivity(), R.id.nav_host_fragment_content_main);
        navController.popBackStack(navController.getGraph().getStartDestinationId(), false);
    }

    @Override
    public void onDestroyView()
    {
        super.onDestroyView();
        binding = null;
    }
}
