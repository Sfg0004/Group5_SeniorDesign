package com.example.uahteam5blockchainapp;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.Toast;
import androidx.core.content.FileProvider;
import androidx.fragment.app.Fragment;
import java.io.File;
import com.example.uahteam5blockchainapp.databinding.FragmentFilesBinding;

public class FilesFragment extends Fragment
{
    private FragmentFilesBinding binding;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState)
    {
        binding = FragmentFilesBinding.inflate(inflater, container, false);
        //Creates a new file object to handle the downloaded files directory
        File directory = new File(requireContext().getExternalFilesDir("/DownloadedFiles").getAbsolutePath());
        //Gets a list of the files in the directory
        File[] filesInDirectory = directory.listFiles();

        //If the result is null, no files have been downloaded
        if (filesInDirectory == null || filesInDirectory.length == 0)
        {
            binding.noFiles.setVisibility(View.VISIBLE);            //Makes the text view visible
            binding.SavedFilesList.setVisibility(View.INVISIBLE);        //Makes the other view invisible
        }
        //Else, there are downloaded files, so process the Array list and show the ones downloaded
        else
        {
            //Gets the linear layout for this fragment
            LinearLayout linearLayout = binding.SavedFilesList;
            //Loops through all files in the directory and adds a button for each
            for (int i = 0; i < filesInDirectory.length; i++)
            {
                final int temp = i;
                //Creates a new button
                Button newButton = new Button(requireContext());
                //Sets the text of the button to the name of the file
                newButton.setText(filesInDirectory[i].getName());
                //Handles what happens when the button is pressed
                newButton.setOnClickListener(new View.OnClickListener() {
                    //Determines what happens when the button is clicked
                    @Override
                    public void onClick(View view)
                    {
                        Log.e("Path to Open", (Uri.fromFile(filesInDirectory[temp])).toString());
                        //Somehow, opens the file
                        openFile(Uri.fromFile(filesInDirectory[temp]));
                    }
                });
                //Adds the new button to the linear layout
                linearLayout.addView(newButton);
            }
            binding.SavedFilesList.setVisibility(View.VISIBLE);        //Makes the view visible
        }

        return binding.getRoot();
    }

    public void onViewCreated(View view, Bundle savedInstanceState)
    {
        super.onViewCreated(view, savedInstanceState);
    }

    //Function to open the file given the URI
    private void openFile(Uri fileLocation)
    {
        //Declares the intent to open the given file
        Intent intent = new Intent(Intent.ACTION_VIEW);
        //Makes a Uri type to handle the file
        Uri fileToOpen = FileProvider.getUriForFile(requireContext(), requireContext().getPackageName() + ".provider", new File(fileLocation.getPath()));
        //Variable holding the type of file to open
        String fileOpenType;
        //If the file ends in pdf, set the open type to pdf
        if (fileLocation.toString().toLowerCase().endsWith(".pdf"))
        {
            fileOpenType = "application/pdf";
        }
        //If the file ends in png, set the open type to png
        else if (fileLocation.toString().toLowerCase().endsWith(".png"))
        {
            fileOpenType = "image/png";
        }
        //If the file ends in jpeg/jpg, set the open type to jpeg
        else if (fileLocation.toString().toLowerCase().endsWith(".jpeg") || fileLocation.toString().toLowerCase().endsWith(".jpg"))
        {
            fileOpenType = "image/jpeg";
        }
        //If the file ends in txt, set the open type to txt
        else if (fileLocation.toString().toLowerCase().endsWith(".txt"))
        {
            fileOpenType = "text/plain";
        }
        //If the file ends in doc/docx, set the open type to microsoft word
        else if (fileLocation.toString().toLowerCase().endsWith(".doc") || fileLocation.toString().toLowerCase().endsWith(".docx"))
        {
            fileOpenType = "application/msword";
        }
        //Else, the file type is unsupported for opening
        else
        {
            //Inform the user of the failure to open the file
            Toast.makeText(requireContext(), "Cannot open file\nUnsupported file type", Toast.LENGTH_LONG).show();
            return;     //Returns control back to the calling program
        }
        //Sets the data for the intent to the Uri location
        intent.setDataAndType(fileToOpen, fileOpenType);
        //Sets the intent's flags to be able to read the file
        intent.setFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        //Tries the activity
        try
        {
            //Starts the activity
            startActivity(intent);
        }
        //If no activity to open the file, then, catch the error and inform the user of the error
        catch (ActivityNotFoundException BigTimeError)
        {
            //Inform the user of the failure to open the file
            Toast.makeText(requireContext(), "No application available to open this file type", Toast.LENGTH_LONG).show();
        }
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();
        binding = null;
    }
}
