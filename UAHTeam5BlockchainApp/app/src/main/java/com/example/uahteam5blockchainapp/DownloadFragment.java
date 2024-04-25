package com.example.uahteam5blockchainapp;

import android.content.ActivityNotFoundException;
import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.core.content.FileProvider;
import androidx.fragment.app.Fragment;
import androidx.navigation.fragment.NavHostFragment;
import com.example.uahteam5blockchainapp.databinding.FragmentDownloadBinding;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.net.URI;
import java.util.ArrayList;

public class DownloadFragment extends Fragment
{
    private PythonCode tempCaller;      //Python function caller code
    private ArrayList<String> availableHashes;      //ArrayList to hold the available hashes for downloading
    private ArrayList<String> hashesToDownload;     //
    private FragmentDownloadBinding binding;
    private int DefaultColor;       //Variable to hold the default color for the list of buttons
    private ArrayList<String> filesToDownload;      //ArrayList of the files the user wants to download
    private ArrayList<String> downloadedFiles;      //ArrayList of the files already downloaded
    private ArrayList<String> possibleFilesToDownload;  //ArrayList of the possible files that can be downloaded from ipfs

    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState)
    {
        binding = FragmentDownloadBinding.inflate(inflater, container, false);
        //Sets the default color to light grey
        DefaultColor = Color.parseColor("#D3D3D3");
        //Creates the PythonCode object to download files
        tempCaller = PythonCode.PythonCode(getContext());
        //Refreshes the blockchain
        tempCaller.refreshBlockchain();
        //ArrayList to hold the hashes to download
        hashesToDownload = new ArrayList<>();
        //Creates an empty list of file names to download
        filesToDownload = new ArrayList<>();
        //Gets a list of the files that have been be downloaded
        downloadedFiles = listFilesInDownloadsDirectory();
        //Gets a list of the URIs corresponding to each downloaded file
        possibleFilesToDownload = tempCaller.listFiles();
        //ArrayList to hold the available hashes to download
        availableHashes = tempCaller.listHashes();

        Log.e("availableHashes:", "" + availableHashes.size());
        for (int i = 0; i < hashesToDownload.size(); i++)
        {
            Log.e("availableHash:", availableHashes.get(i));
            Log.e("correspondingFile:", possibleFilesToDownload.get(i));
        }
        Log.e("availableHashes:", "" + possibleFilesToDownload.size());
        for (int i = 0; i < possibleFilesToDownload.size(); i++)
        {
            Log.e("availableHash:", availableHashes.get(i));
            Log.e("correspondingFile:", possibleFilesToDownload.get(i));
        }
        //If the result is null, no files are available for downloaded
        if (possibleFilesToDownload == null)
        {
            binding.noFiles.setVisibility(View.VISIBLE);                        //Makes the text view visible
            binding.DownloadedFilesList.setVisibility(View.INVISIBLE);          //Makes the other view invisible
            binding.downloadMultipleFiles.setVisibility(View.INVISIBLE);        //Makes the option for downloading multiple files invisible
            binding.DownloadFiles.setVisibility(View.INVISIBLE);                //Marks the download button as invisible

            //Handles what happens when the user presses the done button
            binding.Done.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view)
                {
                    //Navigates back to the First Fragment
                    NavHostFragment.findNavController(DownloadFragment.this).navigate(R.id.action_DownloadFragment_to_FirstFragment);
                }
            });

            //Handles what happens when the user presses the download button when no files can be downloaded
            binding.DownloadFiles.setOnClickListener(new View.OnClickListener()
            {
                @Override
                public void onClick(View view)
                {
                    //Creates an alert dialog to inform the user that there is no files to download
                    AlertDialog.Builder noFilesToDownload = new AlertDialog.Builder(requireContext());
                    noFilesToDownload.setTitle("No Files to Download");
                    noFilesToDownload.setMessage("Redirecting to main view");
                    //Creates the button to for the positive action
                    noFilesToDownload.setPositiveButton("Ok", new DialogInterface.OnClickListener()
                    {
                        public void onClick(DialogInterface logoutDialog, int ID)
                        {
                            //Navigate back to the admin Fragment
                            NavHostFragment.findNavController(DownloadFragment.this).navigate(R.id.action_DownloadFragment_to_FirstFragment);
                        }
                    });
                    //Creates the dialog box
                    AlertDialog reverseDialog = noFilesToDownload.create();
                    //Shows the dialog box
                    reverseDialog.show();
                }
            });
        }
        //Else, there are downloaded files, so process the Array list and show the ones downloaded
        else
        {
            //Gets the linear layout for this fragment
            LinearLayout linearLayout = binding.DownloadedFilesList;
            //Loops through all downloaded files and adds a button for each
            for (int i = 0; i < possibleFilesToDownload.size(); i++)
            {
                //Creates a new button
                Button newButton = new Button(requireContext());
                //Creates a temp string to save the current file name
                String tempName = possibleFilesToDownload.get(i);
                //Sets the text of the button to the name of the file
                newButton.setText(possibleFilesToDownload.get(i));
                //Sets the background for the new button
                newButton.setBackgroundResource(R.drawable.ripple_button);
                //Handles what happens when the button is pressed
                newButton.setOnClickListener(new View.OnClickListener()
                {
                    //Determines what happens when the button is clicked
                    @Override
                    public void onClick(View view)
                    {
                        //If multiple files are to be downloaded, change the color
                        if (binding.downloadMultipleFiles.isChecked())
                        {
                            //Checks if the button has been pressed already, i.e. the current color is blue
                            if (newButton.isSelected())
                            {
                                newButton.setSelected(false);
                                //Change the color to default
                                newButton.setBackgroundColor(DefaultColor);
                                //Remove the filename from the list of files to download
                                filesToDownload.remove(tempName);
                                //Removes the hash of the file from the list of hashes to download
                                hashesToDownload.remove(availableHashes.get(possibleFilesToDownload.indexOf(tempName)));
                            }
                            //Else, the button has not been pressed already
                            else
                            {
                                newButton.setSelected(true);
                                //Changes the color of the button to show it has been selected
                                newButton.setBackgroundColor(Color.parseColor("#0077C8"));
                                //Adds the filename to be opened to the list of files to open
                                filesToDownload.add(tempName);
                                //Adds the hash of the file to the list of hashes to download
                                hashesToDownload.add(availableHashes.get(possibleFilesToDownload.indexOf(tempName)));
                            }
                        }
                        //Else, download the file
                        else
                        {
                            //If the file has already been downloaded, just open it and toast saying the file has already been downloaded
                            if (alreadyDownloaded(tempName))
                            {
                                //Informs the user of the mistake
                                Toast.makeText(getContext(), "File already downloaded. Opening", Toast.LENGTH_SHORT).show();
                                //Opens the file
                                Log.e("DownloadableFile",requireContext().getExternalFilesDir(null) + "/DownloadedFiles/" + tempName);
                                //Creates a new file from the given filename and from the downloaded files directory
                                File tempFile = new File(requireContext().getExternalFilesDir(null) + "/DownloadedFiles/" + tempName);
                                //Creates the Uri from the file
                                Uri fileLocation = Uri.fromFile(tempFile);
                                //Open the selected file
                                openFile(fileLocation);
                            }
                            //Else, the file has not been downloaded, so download it and toast saying the file has been downloaded
                            else
                            {
                                Log.e("DownloadableHash", availableHashes.get(possibleFilesToDownload.indexOf(tempName)));
                                //Downloads the file given the hash and the location where the file will be downloaded
                                tempCaller.downloadFile(availableHashes.get(possibleFilesToDownload.indexOf(tempName)), requireContext().getExternalFilesDir(null) + "/DownloadedFiles/" + tempName, tempName);
                                Toast.makeText(getContext(), "File downloaded. Opening", Toast.LENGTH_SHORT).show();

                                newButton.setBackgroundColor(DefaultColor);
                                newButton.setSelected(false);

                                //Opens the file
                                //Since clicked, empty the list of files to download
                                filesToDownload = new ArrayList<>();
                                //Since clicked, empty the list of hashes to download
                                hashesToDownload = new ArrayList<>();
                                //Creates a new file from the given filename and from the downloaded files directory
                                File tempFile = new File(requireContext().getExternalFilesDir(null) + "/DownloadedFiles/" + tempName);
                                //Creates the Uri from the file
                                Uri fileLocation = Uri.fromFile(tempFile);
                                //Open the selected file
                                openFile(fileLocation);
                            }
                        }
                    }
                });
                //Adds the new button to the linear layout
                linearLayout.addView(newButton);
            }
            binding.DownloadedFilesList.setVisibility(View.VISIBLE);        //Makes the view visible
            binding.noFiles.setVisibility(View.INVISIBLE);                  //Makes the text view invisible
            binding.downloadMultipleFiles.setVisibility(View.VISIBLE);      //Makes the option for downloading multiple files visible
            //Handles what happens when the user presses the download multiple files clicker
            binding.downloadMultipleFiles.setOnClickListener(new View.OnClickListener()
            {
                @Override
                public void onClick(View view)
                {
                    //If the user has just unchecked the list
                    if (!binding.downloadMultipleFiles.isChecked())
                    {
                        //Gets the current linear layout
                        LinearLayout linearLayout = binding.DownloadedFilesList;
                        //Loop through each file in the download list
                        for (int i = 0; i < possibleFilesToDownload.size(); i++)
                        {
                            //Get the current view within the linear layout
                            View childView = linearLayout.getChildAt(i);
                            //If the view is a type of button
                            if (childView instanceof Button)
                            {
                                //Creates a button to manipulate the child view
                                Button currentButton = (Button) childView;
                                //Sets the background color to the default
                                currentButton.setBackgroundColor(DefaultColor);
                                currentButton.setSelected(false);
                            }
                        }
                        //Since clicked, empty the list of files to download
                        filesToDownload = new ArrayList<>();
                        //Since clicked, empty the list of hashes to download
                        hashesToDownload = new ArrayList<>();
                        binding.downloadMultipleFiles.setChecked(false);
                    }
                    //Else, the button has just been clicked
                    else
                    {
                        //Since clicked, empty the list of files to download
                        filesToDownload = new ArrayList<>();
                        //Since clicked, empty the list of hashes to download
                        hashesToDownload = new ArrayList<>();
                        binding.downloadMultipleFiles.setChecked(true);
                    }
                    //MIGHT NEED TO DO SOMETHING HERE

                    //No need to do anything
                }
            });

            //Handles what happens when the user presses the download button
            binding.DownloadFiles.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view)
                {
                    //If the download multiple files is not checked, then post a Toast message telling the user to click on a file to download
                    if (!binding.downloadMultipleFiles.isChecked())
                    {
                        Toast.makeText(getContext(), "Click on file to download", Toast.LENGTH_LONG).show();
                    }
                    //Else, the multiple file download option is checked
                    else
                    {
                        //If no files are selected, put up a toast message
                        if (filesToDownload.isEmpty())
                        {
                            Toast.makeText(getContext(), "Select files to download", Toast.LENGTH_LONG).show();
                        }
                        //Else if only one file is selected, then open it
                        else if (filesToDownload.size() == 1)
                        {
                            Log.e("DownloadableHash", availableHashes.get(possibleFilesToDownload.indexOf(filesToDownload.get(0))));
                            //Downloads the file given the hash and the location where the file will be downloaded
                            tempCaller.downloadFile(availableHashes.get(possibleFilesToDownload.indexOf(filesToDownload.get(0))), requireContext().getExternalFilesDir(null) + "/DownloadedFiles/" + filesToDownload.get(0), filesToDownload.get(0));

                            //Gets the current linear layout
                            LinearLayout linearLayout = binding.DownloadedFilesList;
                            //Loop through each file in the download list
                            for (int i = 0; i < possibleFilesToDownload.size(); i++)
                            {
                                //Get the current view within the linear layout
                                View childView = linearLayout.getChildAt(i);
                                //If the view is a type of button
                                if (childView instanceof Button)
                                {
                                    //Creates a button to manipulate the child view
                                    Button currentButton = (Button) childView;
                                    //Sets the background color to the default
                                    currentButton.setBackgroundColor(DefaultColor);
                                    currentButton.setSelected(false);
                                }
                            }

                            //Creates a new file from the given filename and from the downloaded files directory
                            File tempFile = new File(requireContext().getExternalFilesDir(null) + "/DownloadedFiles/" + filesToDownload.get(0));
                            //Creates the Uri from the file
                            Uri fileLocation = Uri.fromFile(tempFile);
                            //Since clicked, empty the list of files to download
                            filesToDownload = new ArrayList<>();
                            //Since clicked, empty the list of hashes to download
                            hashesToDownload = new ArrayList<>();
                            binding.downloadMultipleFiles.setChecked(false);
                            //Opens the selected file
                            openFile(fileLocation);
                        }
                        //Else, there are multiple files to download, so loop through them and download them
                        else
                        {
                            int numFilesDownloaded = 0;   //Temp int variable to check how many files have been downloaded
                            //Loops through all files to download and downloads them
                            for (int i = 0; i < filesToDownload.size(); i++)
                            {
                                //If the file has not already been downloaded
                                if (!alreadyDownloaded(filesToDownload.get(i)))
                                {
                                    Log.e("DownloadableHash", availableHashes.get(i));
                                    Log.e("DownloadableFile", filesToDownload.get(i));
                                    Log.e("DownloadedHash", availableHashes.get(possibleFilesToDownload.indexOf(filesToDownload.get(i))));
                                    Log.e("DownloadedFile", filesToDownload.get(i));
                                    //Download the file
                                    tempCaller.downloadFile(availableHashes.get(possibleFilesToDownload.indexOf(filesToDownload.get(i))), requireContext().getExternalFilesDir(null) + "/DownloadedFiles/" + filesToDownload.get(i), filesToDownload.get(i));
                                    numFilesDownloaded++;       //Increments the number of files downloaded
                                }
                            }

                            //Changes the background color of the buttons back to normal
                            //Gets the current linear layout
                            LinearLayout linearLayout = binding.DownloadedFilesList;
                            //Loop through each file in the download list
                            for (int i = 0; i < possibleFilesToDownload.size(); i++)
                            {
                                //Get the current view within the linear layout
                                View childView = linearLayout.getChildAt(i);
                                //If the view is a type of button
                                if (childView instanceof Button)
                                {
                                    //Creates a button to manipulate the child view
                                    Button currentButton = (Button) childView;
                                    //Sets the background color to the default
                                    currentButton.setBackgroundColor(DefaultColor);
                                    currentButton.setSelected(false);
                                }
                            }

                            //If no files have been downloaded
                            if (numFilesDownloaded == 0)
                            {
                                //Inform the user that no files have been downloaded
                                Toast.makeText(getContext(),  "Files downloaded previously", Toast.LENGTH_SHORT).show();
                            }
                            //Else, multiple files have ben downloaded
                            else
                            {
                                //Inform the user that x files have been downloaded
                                Toast.makeText(getContext(),  numFilesDownloaded + " files downloaded.\nNow available in the files tab ", Toast.LENGTH_LONG).show();
                            }
                            binding.downloadMultipleFiles.setChecked(false);
                            filesToDownload = new ArrayList<>();      //Empties and creates a new empty list of files to download
                            hashesToDownload = new ArrayList<>();       //Empties and creas a new empty list of hashes to download
                        }
                    }
                }
            });

            //Handles what happens when the user presses the done button
            binding.Done.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view)
                {
                    //Navigates back to the First Fragment
                    NavHostFragment.findNavController(DownloadFragment.this).navigate(R.id.action_DownloadFragment_to_FirstFragment);
                }
            });
        }
        return binding.getRoot();
    }

    public void onViewCreated(@NonNull View view, Bundle savedInstanceState)
    {
        super.onViewCreated(view, savedInstanceState);
        //There is no need to ensure the file "downloadeduris.txt" exists, because if it does not, a different view will be enabled
    }

    //Function to check if the
    public boolean alreadyDownloaded(String filename)
    {
        //Loops through the list of downloaded files
        for (int i = 0; i < downloadedFiles.size(); i++)
        {
            //If the current item has the same filename
            if (downloadedFiles.get(i).equals(filename))
            {
                return true;        //Returns true to show that the file is already downloaded
            }
        }
        //Else, the file is not downloaded
        return false;
    }

    //Function to read the Uris from the uri download file
    //And return the name as strings
    private ArrayList<String> readDownloadedFiles(String filePath)
    {
        ArrayList<String> filenameList = new ArrayList<>();      //Creates a new ArrayList for the Uris
        File testFile = new File(filePath);     //Tries to create a file handler to the file path
        //If the file does not exist...
        if (!testFile.exists())
        {
            return null;    //Returns null value to show that no files have been downloaded
        }
        try
        {
            //Create new file and buffer reader to process the file
            FileReader fileReader = new FileReader(filePath);
            BufferedReader bufferedReader = new BufferedReader(fileReader);
            String UriLine = bufferedReader.readLine();     //Reads the first line from the file
            //Loops through the entire file and collects the Uris
            while (UriLine != null)
            {
                String[] fileName = UriLine.split("/");
                filenameList.add(fileName[fileName.length-1]);       //Adds the new URI to the end of the list
                UriLine = bufferedReader.readLine();     //Reads the next line from the file
            }
            //Closes the connection to the file handlers
            fileReader.close();
            bufferedReader.close();
        }
        //Catches an exception with reading the file
        catch (IOException error)
        {
            Toast.makeText(getContext(), "Runtime exception", Toast.LENGTH_LONG).show();
            throw new RuntimeException();       //Throws an exception as an error occurred
        }
        return filenameList;     //Returns the list of URIs
    }

    //Function to read and returns the Uris from the given file
    public ArrayList<URI> readUrisFromFile(String filename)
    {
        ArrayList<URI> UriList = new ArrayList<>();      //Creates a new ArrayList for the Uris
        File testFile = new File(filename);     //Tries to create a file handler to the file path
        //If the file does not exist...
        if (!testFile.exists())
        {
            return null;    //Returns null value to show that no files have been downloaded
        }
        try
        {
            //Create new file and buffer reader to process the file
            FileReader fileReader = new FileReader(filename);
            BufferedReader bufferedReader = new BufferedReader(fileReader);
            String UriLine = bufferedReader.readLine();     //Reads the first line from the file
            //Loops through the entire file and collects the Uris
            while (UriLine != null)
            {
                UriList.add(URI.create(UriLine));       //Adds the new URI to the end of the list
                UriLine = bufferedReader.readLine();     //Reads the next line from the file
            }
            //Closes the connection to the file handlers
            fileReader.close();
            bufferedReader.close();
        }
        //Catches an exception with reading the file
        catch (IOException error)
        {
            Toast.makeText(getContext(), "Runtime exception", Toast.LENGTH_LONG).show();
            throw new RuntimeException();       //Throws an exception as an error occurred
        }
        return UriList;     //Returns the list of URIs
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

    //Function to read and list the files in a directory
    public ArrayList<String> listFilesInDownloadsDirectory()
    {
        //Variable to hold the list of filenames for the files downloaded
        ArrayList<String> resultingFileNames = new ArrayList<String>();
        //Creates a new file to handle the list of downloaded files
        File directoryFiles = new File(requireContext().getExternalFilesDir(null) + "/DownloadedFiles/");
        //Converts the directory as a file into the list of directory files
        File[] filesInDirectory = directoryFiles.listFiles();
        //If no files in the directory
        if (filesInDirectory == null)
        {
            return null;        //Returns null to show no files in the directory
        }
        //Else, there are files in the directory
        else
        {
            //Loops through the entire directory and pulls the file names
            for (int i = 0; i < filesInDirectory.length; i++)
            {
                //Adds the current file name to the list of downloaded files
                resultingFileNames.add(filesInDirectory[i].getName());
            }
        }
        return resultingFileNames;      //Returns the list of resulting file names
    }

    @Override
    public void onDestroyView() {
        super.onDestroyView();

        //Gets the current linear layout
        LinearLayout linearLayout = binding.DownloadedFilesList;
        //Loop through each file in the download list
        for (int i = 0; i < possibleFilesToDownload.size(); i++)
        {
            //Get the current view within the linear layout
            View childView = linearLayout.getChildAt(i);
            //If the view is a type of button
            if (childView instanceof Button)
            {
                //Creates a button to manipulate the child view
                Button currentButton = (Button) childView;
                //Sets the background color to the default
                currentButton.setBackgroundColor(DefaultColor);
                currentButton.setSelected(false);
            }
        }

        possibleFilesToDownload = new ArrayList<>();
        availableHashes = new ArrayList<>();
        binding.downloadMultipleFiles.setChecked(false);
        //Since clicked, empty the list of files to download
        filesToDownload = new ArrayList<>();
        //Since clicked, empty the list of hashes to download
        hashesToDownload = new ArrayList<>();

        binding = null;
    }
}
//file uri is saved here, and here is how to get its location
//
//String filename = requireContext().getExternalFilesDir(null) + "/data/uploadeduris.txt";
//String filename = requireContext().getExternalFilesDir(null) + "/data/downloadeduris.txt";
//