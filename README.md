# MULTIPLYVisualisation

# Installation
* Install conda
  * Open a terminal with the user that will be running the MULTIPLY Visualisation 
  * ```wget https://repo.continuum.io/miniconda/Miniconda3-4.7.12-Linux-x86_64.sh```
  * ```bash Miniconda3-4.7.12-Linux-x86_64.sh```
  * close this terminal and open a new one for the following steps
  
* Clone the git remote repository, use the specific branch
  * ```git clone -b fernando_scratch --single-branch https://github.com/Assimila/MULTIPLYVisualisation.git```
  * Create the required conda environment
    * ```cd MULTIPLYVisualisation```
    * ```conda create -n multiply_vis --file MULTIPLYvisualisation_env.txt```
    
* Run the MULTIPLY Visualisation
  * Set IP address where to run the server
    * Edit the src/MultiplyVis.py
      * In line 50, change the host parameter with the VM internal IP address, for instance 10.154.0.2:
        * ```app.run_server(debug=True, host='10.154.0.2')```
      * By default DASH uses port 8050, open that port in the firewall. If a different port is needed, add the port when calling the server:
        * ```app.run_server(debug=True, host='10.154.0.2', port=8051)```
        
    * Locate the MULTIPLY output directory. The MULTIPLY Vis still uses KaFKA outputs, one file per time step!, e.g.:
      * A couple of months data:
        * ```/home/user/MULTIPLYVisualisation/data```
      * About six months data:
        * ```/home/user/MULTIPLYVisualisation/data_2```
    
    * Activate the conda environment
      * ```conda activate multiply_vis```
     
    * Start the server
      * ```python MVis.py /home/lopez_saldana/MULTIPLYVisualisation/data_2```
      * Open a browser and go to the VM external IP address, e.g. 35.230.135.32 and port 8050
        * http://35.230.135.32:8050
