package com.example.uahteam5blockchainapp;

import static android.app.Activity.RESULT_OK;
import android.icu.text.SimpleDateFormat;
import android.net.Uri;
import android.os.Bundle;
import android.database.Cursor;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.Manifest;
import androidx.fragment.app.Fragment;
import androidx.navigation.fragment.NavHostFragment;
import android.content.Intent;
import android.graphics.Bitmap;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import android.provider.MediaStore;
import android.widget.Toast;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Arrays;
import java.util.Calendar;  //Imports the calendar to get the date
import java.util.Date;      //Gets the date
import java.util.Locale;

import com.example.uahteam5blockchainapp.databinding.FragmentUploadBinding;


public class UploadFragment extends Fragment {
    private ActivityResultLauncher<Intent> cameraLauncher;
    private ActivityResultLauncher<String> requestPermissionLauncher;
    private ActivityResultLauncher<Intent> pickFileLauncher;
    private ActivityResultLauncher<Intent> pickPhotoLauncher;

    private FragmentUploadBinding binding;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        binding = FragmentUploadBinding.inflate(inflater, container, false);
        return binding.getRoot();
    }

    @Override
    public void onViewCreated(View view, Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        //Result launcher to pick the uri to send on from photos
        pickPhotoLauncher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(), result ->
        {
            //If the photo picker was successful, then proceed with processing the image
            if ((result.getResultCode() == RESULT_OK) && (result.getData() != null))
            {
                //Gets the resulting image from the photo gallery
                Uri selectedImageUri = result.getData().getData();
                processImage(selectedImageUri);     //Calls the function to process the image and send it onto the next fragment
            }
            else
            {
                //Sends a toast message to inform the user that
                Toast.makeText(getContext(), "Something unexpected happened", Toast.LENGTH_SHORT).show();
            }
        });

        //Result launcher for camera permission
        cameraLauncher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(), result -> {
            //If the operation succeeded, then continue with processing the image
            if ((result.getResultCode() == getActivity().RESULT_OK) && (result.getData() != null))
            {
                //Gets the resulting image from the camera
                Intent data = result.getData();
                Bitmap imageBitmap = (Bitmap) data.getExtras().get("data");     //Gets the resulting Bitmap image

                //Creates new current calendar instance and new date instance to name the file
                Calendar calendar = Calendar.getInstance();
                Date currentDate = calendar.getTime();
                //Gets the current date time format and processes the current time zone
                SimpleDateFormat dateFormat = new SimpleDateFormat("MM-dd-yyyy HH:mm:ss", Locale.getDefault());
                String fileName = dateFormat.format(currentDate).replaceFirst(" ", "_") + ".png";       //Creates a file name for the new image with the current date and time (in the current Timezone)
                File newFile = new File(requireContext().getExternalFilesDir("SavedImages"), fileName);      //Saves the Bitmap to a file

                //Tries to write the image to an output file
                try
                {
                    FileOutputStream outputStream = new FileOutputStream(newFile);      //Creates a new output stream to handle the new file being created
                    imageBitmap.compress(Bitmap.CompressFormat.PNG, 100, outputStream);     //Compresses the file into png format and sends it to the output stream
                    outputStream.flush();       //Flushes the output stream
                    outputStream.close();       //Closes the output stream
                    processImage(Uri.fromFile(newFile));        //Sends the Uri of the new file to be processed by the process image function
                }
                //Catches a write error
                catch (IOException error)
                {
                    Toast.makeText(getContext(), "Error saving image", Toast.LENGTH_SHORT).show();
                    //Potential issue to look into: if issue, might need to redirect to the first fragment
                }
            }
            //Else, something went wrong with the camera
            else
            {
                //Else, camera permission is denied so make the user understand
                Toast.makeText(requireContext(), "Issue capturing image", Toast.LENGTH_LONG).show();
            }
        });

        //Launcher to request permission to use the camera. If permission is granted, launch the camera launcher
        requestPermissionLauncher = registerForActivityResult(new ActivityResultContracts.RequestPermission(), isGranted ->
        {
            //If permission is grated to use the camera, open the camera, take a picture, confirm the picture, and process the picture
            if (isGranted)
            {
                //Creates an intent to take a picture
                Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
                //Calls the camera launcher telling it to take a picture
                cameraLauncher.launch(takePictureIntent);
            }
            //Else, permission is denied to use the camera, so inform the user that this permission is required for this feature
            else
            {
                //Sends a toast message to inform the user that they need to give permission to use this feature
                Toast.makeText(getContext(), "Camera permission required\n  to use this feature", Toast.LENGTH_LONG).show();
            }
        });

        //Launcher to handle an incoming file
        pickFileLauncher = registerForActivityResult(new ActivityResultContracts.StartActivityForResult(), result->
        {
            //Checks if the result is good and data has resulted
            if (result.getResultCode() == RESULT_OK)
            {
                Intent resultingData = result.getData();     //Gets the data from the result
                //If the resulting data is null, don't process the image
                if (resultingData.getData() != null)
                {
                    processImage(resultingData.getData());       //Sends a Uri to be processed
                }
            }
            //Else, no file was selected, so inform the user
            else
            {
                Toast.makeText(getContext(), "No file selected", Toast.LENGTH_SHORT).show();
            }
        });

        binding.UploadPhoto.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
                requestCameraPermission();  //Requests permission to use the camera. If permission is had already,
            }
        });

        //Binds the button to the function to open the photos app
        binding.UploadCameraRoll.setOnClickListener(new View.OnClickListener()
        {
            //Overrides the action when the button is pressed
            @Override
            public void onClick(View view)
            {
                //Calls the function to get the photo from the photo reel and to process it
                openPhotos();
            }
        });

        //Function to handle when the upload from device button is selected
        binding.UploadFromDevice.setOnClickListener(new View.OnClickListener()
        {
            @Override
            public void onClick(View view)
            {
                //Calls the function to get a file to open
                openFile();
            }
        });

    }

    //Function to open the file picker
    private void openFile()
    {
        Intent pickFileIntent = new Intent(Intent.ACTION_OPEN_DOCUMENT);        //Creates a new intent to open a file
        pickFileIntent.addCategory(Intent.CATEGORY_OPENABLE);               //Adds the intent to the file picker
        pickFileIntent.setType("*/*");                                  //Sets the acceptable file types
        pickFileLauncher.launch(pickFileIntent);                    //Launches the file picker launcher
    }

    //Function to open the camera roll, or the photo app
    private void openPhotos()
    {
        //Declares the intent to open the photos API to get images from the device directly
        Intent pickPhotoIntent = new Intent(Intent.ACTION_PICK);
        pickPhotoIntent.setType("image/*");     //Looks for an image
        //Uses the result launcher to pick a photo from the photos gallery
        pickPhotoLauncher.launch(pickPhotoIntent);
    }

    //Function to process the image taken from the camera
    //Next version, second parameter, a file/filepath, one of the two is null. send the new data to the next fragment
    //Which uploads to the blockchain
    private void processImage(Uri takenImage)
    {
        //If no image was taken, or data provided, then send the Uri onto the next fragment
        if (takenImage == null)
        {
            Toast.makeText(getContext(), "Nothing to add", Toast.LENGTH_SHORT).show();
        }
        else //Else, the taken image was not null, so it is to be added to the blockchain
        {
            Calendar calendar = Calendar.getInstance();
            Date currentDate = calendar.getTime();
            SimpleDateFormat dateFormat = new SimpleDateFormat("MM-dd-yyyy HH:mm:ss", Locale.getDefault());
            //Creates a file name for the new image with the current date and time (in the current Timezone)
            String fileName = dateFormat.format(currentDate).replaceFirst(" ", "_") + ".png";
            //If no data is provided to the function, send out a toast message saying data cannot be added as it does not exist

            String filePath = getFilePathFromUri(takenImage);

            ConfirmUploadFragment newFragment = new ConfirmUploadFragment();        //Creates the next fragment variable
            Bundle arguments = new Bundle();        //Creates a new bundle of arguments to send
            arguments.putString("uri", takenImage.toString());  //Adds the uri to the bundle///////////////takenImage.toString()(or.toPath)
            newFragment.setArguments(arguments);        //Sends the arguments to the next fragment
            //Calls the action and sends control to the confirm upload fragment
            NavHostFragment.findNavController(UploadFragment.this).navigate(R.id.action_UploadFragment_to_ConfirmUploadFragment, arguments);
        }
    }

    private String getFilePathFromUri(Uri takenImage)
    {
        String finalPath = "";
        if ("content".equalsIgnoreCase(takenImage.getScheme()))
        {
            String[] projection = {MediaStore.Images.Media.DATA};
            try
            {
                Cursor cursor = getContext().getContentResolver().query(takenImage, projection, null, null, null);
                if (cursor != null && cursor.moveToFirst());
                {
                    int columnIndex = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATA);
                    finalPath = cursor.getString(columnIndex);
                }

            }
            //Catches any issues that occur with the previous block
            catch (Exception error)
            {
                Log.e("Upload Fragment Error", Arrays.toString(error.getStackTrace()));
            }

        }
        else if ("file".equalsIgnoreCase(takenImage.getScheme()))
        {
            finalPath = takenImage.getPath();
        }
        //Returns the final path from the given Uri
        return finalPath;
    }

    //Function to request permission to use the camera
    private void requestCameraPermission()
    {
        requestPermissionLauncher.launch(Manifest.permission.CAMERA);       //Launches the permission request form
    }

    //Function to destroy the view and delete the view elements when it is left
    @Override
    public void onDestroyView()
    {
        super.onDestroyView();
        binding = null;
    }
}


/*

Notes, when I hit upload, upload from photos, it works and forwards me.  Same for uploading a file from the device. Same for uploading from camera live.
//Thoughts, save files in the savedFiles directory
//Have .data directory for keys and such

 */