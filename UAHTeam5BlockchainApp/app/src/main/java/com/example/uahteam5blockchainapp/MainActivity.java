package com.example.uahteam5blockchainapp;

import android.content.DialogInterface;
import android.os.Bundle;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;
import androidx.navigation.ui.AppBarConfiguration;
import androidx.navigation.ui.NavigationUI;
import com.example.uahteam5blockchainapp.databinding.ActivityMainBinding;
import android.widget.Toast;

public class MainActivity extends AppCompatActivity {

    private AppBarConfiguration appBarConfiguration;
    private ActivityMainBinding binding;

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        binding = ActivityMainBinding.inflate(getLayoutInflater());
        //Initializes the python code caller overall
        PythonCode tempCaller = PythonCode.PythonCode(getApplicationContext());
        //Loads the blockchain into the PythonCode class
        tempCaller.start();
        setContentView(binding.getRoot());
        setSupportActionBar(binding.toolbar);
        NavController navController = Navigation.findNavController(this, R.id.nav_host_fragment_content_main);
        appBarConfiguration = new AppBarConfiguration.Builder(navController.getGraph()).build();
        NavigationUI.setupActionBarWithNavController(this, navController, appBarConfiguration);
    }

    @Override
    public boolean onSupportNavigateUp() {
        NavController navController = Navigation.findNavController(this, R.id.nav_host_fragment_content_main);
        //If the user presses the back button when on the first fragment, pop up a message confirming logout, and if yes, then logout
        if ((navController.getCurrentDestination() != null) && (navController.getCurrentDestination().getId() == R.id.FirstFragment))
        {
            confirmLogout();        //Invoke logout method
            return true;            //Returns true to show the navigation has been taken care of
        }
        //If the user presses the back button when on the admin fragment, pop up a message confirming logout, and if yes, then logout
        if ((navController.getCurrentDestination() != null) && (navController.getCurrentDestination().getId() == R.id.AdminFragment))
        {
            confirmLogout();        //Invoke logout method
            return true;            //Returns true to show the navigation has been taken care of
        }
        //If the user presses the back button when on the upload finish fragment,go back to the first fragment
        if ((navController.getCurrentDestination() != null) && (navController.getCurrentDestination().getId() == R.id.UploadFinishFragment))
        {
            goToFirst();            //Navigates back to the first fragment
            return true;            //Returns true to show the navigation has been taken care of
        }
        //If the user presses the back button to get back to confirm upload fragment, then prevent the action
        if ((navController.getCurrentDestination() != null) && (navController.getCurrentDestination().getId() == R.id.ConfirmUploadFragment))
        {
            //Creates an alert dialog to confirm cancellation that
            AlertDialog.Builder builder = new AlertDialog.Builder(this);
            builder.setTitle("Cancel Upload");
            builder.setMessage("Are you sure you want to cancel?");
            //Creates two buttons
            //Creates the button to for the positive action
            builder.setPositiveButton("Yes", new DialogInterface.OnClickListener()
            {
                public void onClick(DialogInterface logoutDialog, int ID)
                {
                    //Navigate back up a fragment
                    goToFirst();            //Navigates back to the first fragment
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
            return true;            //Returns true to show the navigation has been taken care of
        }
        //Else, allow the navigation to continue up
        return NavigationUI.navigateUp(navController, appBarConfiguration) || super.onSupportNavigateUp();
    }

    //Function to confirm the user wants to logout
    private void confirmLogout()
    {
        //Creates an alert dialog to show that
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Confirm Logout");
        builder.setMessage("Are you sure you want to logout?");
        //Creates two buttons
        //Creates the button to for the positive action
        builder.setPositiveButton("Yes", new DialogInterface.OnClickListener()
        {
            public void onClick(DialogInterface logoutDialog, int ID)
            {
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

    //Function to return control back to the login fragment
    private void returnToLoginFragment()
    {
        //Inform the user that the logout was successful
        Toast.makeText(getApplicationContext(), "Logout Successful", Toast.LENGTH_SHORT).show();
        //Navigates back to the login Fragment
        NavController navController = Navigation.findNavController(this, R.id.nav_host_fragment_content_main);
        navController.popBackStack(navController.getGraph().getStartDestinationId(), false);
    }

    //Function to return control back to the login fragment
    private void goToFirst()
    {
        //Navigates back to the first Fragment
        NavController navController = Navigation.findNavController(this, R.id.nav_host_fragment_content_main);
        navController.navigate(R.id.FirstFragment);
    }
}