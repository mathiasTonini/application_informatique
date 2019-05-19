<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>baby mind web interface -result</title>
</head>
<?php

// Get the values from the html form
$dac=$_POST['dac'];
$time=$_POST['time'];
$choice=$_POST['choice'];
$drawFrom=$_POST['thresholdFrom'];
$drawTo=$_POST['thresholdTo'];
$step=$_POST['step'];
$tableOfFile=$_FILES["upload"];
$total = count($_FILES["upload"]["name"]);
$target='/uploads';

//define default values

if ($drawFrom== NULL){
	echo 'default value for threshold from=100 </br>';
	$drawFrom=100;
}
else{
	echo 'Value for thresold from: '.$drawFrom.'</br>';
}
if ($drawTo==NULL){
	echo 'default value for threshold to=200 </br>';
	$drawFrom=200;
}
else{
	echo 'Value for thresold to: '.$drawTo.'</br>';
}
if ($step==NULL){
	echo 'default value for step =20 </br>';
	$drawFrom=20;
}
else{
	echo 'Value for the step: '.$step.'</br>';
}
if ($choice==NULL){
	echo 'default value for choice HG </br>';
	$choice="HG";
}
else{
	echo 'You choose: '.$choice.'</br>';
}
if ($time==NULL){
	echo 'default value for time =4000 </br>';
	$time=4000;
}
else{
	echo 'Value for the time: '.$time.'</br>';
}

//Create unique directory
$dir="./uploads/".rand();
	while (is_dir($dir))
	{
		$dir="./uploads/".rand();
	}
mkdir($dir);

// Verify if files are daq, if not just delete them, if yes copy them to normal file for python script
if ($_POST['data_base_or_upload']=='files'){
	for ($i=0;$i < $total; $i++){
		if ($_FILES["upload"]['type'][$i]=='application/octet-stream'){
			$tempPath=$_FILES["upload"]['tmp_name'][$i];
			$path=$dir."/".$_FILES["upload"]['name'][$i];
			if(copy($tempPath, $path)){
				unlink($tempPath);
			}
		}else{
			echo 'file deleted: '.$_FILES["upload"]["name"];
			$tempPath=$_FILES["upload"]['tmp_name'][$i];
			unlink($tempPath);
		}
	}
}

//Create command to exec the python script
if ($_POST['data_base_or_upload']=='files'){

	$commande="python drawCosmicFlux.py ".$dir." ".$drawFrom." ".$drawTo. " ".$step." ".$dac. " ".$choice. " ".$time." 0 test"; //Last 0 means that we use uploaded files
	echo "running ".$commande. " ... </br>";
	ob_flush();
	flush();
}
elseif($_POST['data_base_or_upload']=='data'){
	$date=$_POST['year'].'-'.$_POST['month'].'-'.$_POST['day']; //make date as Year-mont-day
	$findFiles='data-'.$date;
	echo $findFiles.'</br>';
	$commande="python drawCosmicFlux.py ".$dir." ".$drawFrom." ".$drawTo. " ".$step. " ".$dac." ".$choice. " ".$time." 1 ".$findFiles; //Last  means that we use uploaded files
	echo "running ".$commande. " ... </br>";
	ob_flush();
	flush();
}

$output= exec($commande). "</br>";
if ($output != 'end') //
{
	echo ' Sorry, something went wrong with the python script </br'.$output.'</br>';
}

ob_flush();
flush();

//////Récupération des images
$images=$dir.'/figures';
if($dossier = opendir($images)){
	$counter=0;
	while(false !== ($fichier = readdir($dossier))){
		if ($fichier != '.' && $fichier != '..'){
			 $source=$images."/".$fichier;
			 $counter++;
			//echo "source: .".$source;
			echo
				"<a href=\"".$source."\" download> Download ".$fichier."</a></br>"; //Download file
			echo

				"<img
				src=\"".$source."\"
				alt=\"".$fichier."\"
				height=\"500px\"
				width=\"500px\" />";
			echo
				"</br>";
		}
	}
	if ($counter==0){
		echo "something went wrong with the script </br>";
	}
}
closedir($dossier);
ob_flush();
flush();




//Uncomment this part to clean files once user is disconnected


ignore_user_abort(True);
// Start infinite boucle
while (1){
	if (connection_aborted()){
		$test=fopen('test.txt','w+');
		fwrite($test,connection_status());
		fclose($test);
		//delet plot
		if($dossier = opendir($images)){
			while(false !== ($fichier = readdir($dossier))){
				$source=$images."/".$fichier;
				unlink($source); // Supprimer tous les fichiers dans figures
			}
		}
		closedir($dossier);
		rmdir($images); //supprimer le dossier figures

		//delete temp folder
		if($dossier = opendir($dir)){
			while(false !== ($fichier = readdir($dossier))){
				$source=$dir."/".$fichier;
				unlink($source); // Supprime les fichiers daq
			}
		}
		closedir($dossier);
		rmdir($dir);
		exit;
	}else{
		echo "</br>";
		ob_flush();
		flush();
		sleep(1); // wait until connection is aborded
	}
}

 ?>
