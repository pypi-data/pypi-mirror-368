# RDEER-SERVICE

rdeer-service is a tool to facilitate the use of [Reindeer](https://github.com/kamimrcht/REINDEER) as a socket mode. It allows multiple Reindeer indexes to be loaded into memory, spread over several servers, enabling queries to be made quickly and easily.

It consists of a server part: **rdeer-server**, one instance of which will be started per index server, and a client part: **rdeer**, which allows index manipulation (stopping, starting, etc.) and queries.

It is a companion to [Transipedia](https://transipedia.org), a web application for querying Reindeer but it may be useful to use it independently.


### Prerequisite

- Reindeer must be installed on indexes servers and the **reindeer_socket** binary in your $PATH
- You need some Reindeer indexes (Stored on SSD disks to better performances, otherwise build indexes with the Reindeer `--mem-query` option).

## Installation

**Recommanded (pip)**

```
python3 -m pip install rdeer-service
```

**Other (git)**

```
git clone https://github.com/Bio2M/rdeer-service.git
```


## How to use?


### Start the server

rdeer-server requires Reindeer to be installed on the same physical machine. There can be several instances of rdeer-server running on the same server, each instance listening on a different TCP port (`-p` option). rdeer-client can query remote servers, so you can have multiple servers hosting rdeer-server/Reindeer and query them all from the same machine.

```
rdeer-server /path/to/indexes
```

* rdeer-server listen on port 12800, you can change this with `--port` option.
* The server will only be able to handle indexes in the specified directory. If your indexes are spread over several directories, you may create symlinks in `/path/to/indexes`.
* You can add, remove or change the name of the indexes, rdeer-server takes the changes on the fly.
* It is recommended to start rdeer-server as a daemon, using systemd, supervisord or similar.

#### notifications

rdeer try to restart the indexes cyclically when error stastus


### Use the client

The client could requests remote rdeer-server servers. You can enterely manage yours distributed Reindeer indexes with subcommand:

* `rdeer list -a` to show all indexes with their status
* `rdeer start <index-name>` to start a index (the index name is the directory hosting the index files)
* `rdeer stop <index-name>` to stop a index.
* `rdeer kill <index-name>` If the index crashes during loading, rdeer-server will try to restart.
it cyclically. The stop option cannot be used during loading, so the kill option must be used.
* `rdeer check <index-name>` to verify if index responding.
* `rdeer status <index-name>` to get the index status (available, loading, running, error).
* `rdeer query <index-name> -q <query.fa>` to request an index.


**show running indexes:**

```
rdeer-client list
```

**Show all indexes handled by rdeer-server**

```
rdeer-client list -a
```

list all accessible indexes by rdeer-server, with status. Status are : 

* `available` the index is not running
* `loading` the index is in a transitional mode until the running mode
* `running` the index is started, and can be resquested.
* `error` a error occured on the index.


**Start an index:**

```
rdeer-client start my-index
```

Will starts the **my-index** Reindeer index. When status is `running`, the index is ready to respond to requests.

**Query an index**

```
rdeer-client query my-index -q fasta-query
```

Requests the specified index, the query file is required and must be in a fasta format.

Options of query subcommand (`rdeer-client query --help`):

* `-q/--query` to send a query file at the fasta format (**required**)
* `-f/--format {raw,sum,average,mean,normalize}` where
    * `raw` to get results 
    * `sum` to get sum of kmer counts
    * `mean`, `average` to get sum of kmer counts / number of kmers
    * `normalize` to get normalized counts as billion of kmers
* `-s/--server` to request rdeer-server on remote host
* `-p/--port` to request rdeer-server on a specified port (default: 12800)
* `-o/--outfile` output is stdout by default, you can specified a file

