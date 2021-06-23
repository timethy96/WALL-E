<?php

date_default_timezone_set("Europe/Berlin");

?>
<!DOCTYPE HTML>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>WALL-E</title>
        <meta name="description" content="Website of the WALL-E-Project">
        <meta name="author" content="Timo Bilhöfer">
        <link rel="icon" type="image/png" href="img/logo.png">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <link rel="stylesheet" href="css/styles.css" />
    </head>
    <body>
        <div id="main">
            <h1>WALL-E</h1>
            <p>Select upload type:</p>
            <div id="ulType">
                <button id="bImgUl">Image upload</button>
                <button id="bVidUl">Video upload</button>
                <button id="bDrawUl">Drawing</button>
            </div>
            <div id="imgUl" class="hidden ul">
                <form action="<?php echo $_ENV['APIURL'] ?>" method="post" class="ulForm" enctype="multipart/form-data"> 
                    <label>Select a file: <input type="file" name="in_file"/></label>
                    <label>How long should the image be shown: <select name="length">
                        <option value="10">10s</option>
                        <option value="20">20s</option>
                        <option value="30">30s</option>
                    </select></label> 
                    <label>Daily recurring image: <input type="checkbox" value="1" name="recurring"/></label>
                    <label>When should the image be shown (leave empty for ASAP): <input type="time" name="time" /></label>
                    <input type="submit" value="Upload" />               
                </form>
                <div class="ulStatus">
                    <img src="" class="loading hidden" alt="loading" />
                    <p class="responseText"><p>
                </div>
            </div>
            <div id="vidUl" class="hidden ul">
                <form action="<?php echo $_ENV['APIURL'] ?>"  method="post" class="ulForm" enctype="multipart/form-data">
                    <label>Select a file: <input type="file" name="in_file"/></label>
                    <label>Daily recurring video: <input type="checkbox" value="1" name="recurring" /></label>
                    <label>When should the video be shown (leave empty for ASAP): <input type="time" name="time" /></label>
                    <input type="submit" value="Upload" />               
                </form>
                <div class="ulStatus">
                    <img src="" class="loading hidden" alt="loading" />
                    <p class="responseText"><p>
                </div>
            </div>
            <div id="drawUl" class="hidden ul">
                <p>Coming soon...</p>
            </div>
            <h2>Queue:</h2>
            <div id="queueDiv">
                
                <?php
                    $queue = json_decode(file_get_contents($_ENV['APIURL']."/queue/"), true);
                    if ($queue != ""){
                        foreach ($queue as $qMov) {
                            $qmFilename = explode("/", $qMov["filePath"]);
                            ?>
                            <div class="qMov">
                                <img src="" alt="Movie-Thumbnail">
                                <div class="qmInfo">
                                    <?php
                                    echo "<p>".end($qmFilename)."</p>";
                                    echo "<p>".date("H:i - d.m.y",$qMov["dTime"])."</p>"; 
                                    ?>
                                </div>
                            </div>
                            <?php
                        }
                    }

                ?>
            </div>
        </div>
        <script src="js/jquery-3.6.0.min.js"></script>
        <script src="js/main.js"></script>
    </body>
</html>