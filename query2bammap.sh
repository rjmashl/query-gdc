#!/bin/bash

# 2021-09-08: rewrite to include new features useful for various workflows

#project_id      file_id file_name       submitter_id    aliquot_id_list sample_name_list        sample_type_list        preservation_method_list        data_category   data_type       caller  call_format     experimental_strategy

export QUERY_RESULTS=query_results.fixed.tsv
export GDC_MANIFEST=gdc_manifest.2021-08-21.txt
export REFERENCE_SHORT=hg38

perl -e ' %h=();

# store md5,size
open(IN, "<",  $ENV{GDC_MANIFEST});
while(<IN>) {
  next if( /^id/ || /^project/);
  chomp;
  ($gdc_file_id, $filename, $md5, $size, $state) = split /\t/;
  $h{ $filename } = {'md5' => $md5, 'size' => $size, 'gdc_file_id' => $gdc_file_id };
}
close(IN);


open(IN, "<",  $ENV{QUERY_RESULTS});
$bHead = 1;
while(<IN>){
 chomp;
 ($project_id, $gdc_file_id, $gdc_filename, $submitter_id,  $aliquot_id_list,  $sample_name_list, $sample_type_list, $preservation_method_list, $data_category, $data_type, $caller, $call_format, $experimental_strategy) = split/\t/;

if ( $call_format eq "BAM"  &&  $data_category eq "Sequencing Reads" && $data_type eq "Aligned Reads") {

   $cluster = "NULL";

  $parent_dir = "NULL";
  if ($project_id =~ /DLBCL/ ) {
     $parent_dir = "/storage1/fs1/dinglab/Active/Primary/CTSP-DLBCL/GDC/aligned_reads_by_case/$submitter_id";
     $cluster = "storage1";
  }


  $md5 = "NA";
  $size = "NA";
  if(exists  $h{$gdc_filename} ) {
     $md5 = $h{$gdc_filename}{'md5'};
     $size = $h{$gdc_filename}{'size'};

     # check for mismatch between data sources
     if( $gdc_file_id  ne  $h{$gdc_filename}{'gdc_file_id'} ) {
        print "ERROR: GDC file id mismatch at filename  $gdc_filename. Exiting.\n";
     }
  }


   #
   # transform to alternative names
   # remap; must coordinate with TinDaisy setup
   #
    $sample_type_group = "NULL";
      if( $sample_type_list =~ /normal/i ) {
          if( $sample_type_list =~ /blood/i ) {
             $sample_type_group = "blood_normal";
             $sample_type_letter = "N";
          } elsif ( $sample_type_list =~ /tissue/i ) {
             $sample_type_group = "tissue_normal";
             $sample_type_letter = "A";
          } else {
            print "ERROR: normal sample type $sample_type_list is one i do not recognize. Exiting.\n";
            exit(1);
         }
      } elsif ( $sample_type_list =~ /tumor/i  ||  $sample_type_list =~ /slides/i || $sample_type_list =~ /scrolls/i ) {
            $sample_type_group = "tumor";
             $sample_type_letter = "T";
      } else {
            print "ERROR: sample type $sample_type_list is one i do not recognize. Exiting.\n";
            exit(1);
     }


     $alt_sample_name = join(".", $sample_name_list, lc( $experimental_strategy ), $sample_type_letter, $ENV{REFERENCE_SHORT} );

     $disease = "NA";   # Note: depends on project (may have multiple types), diagnosis subtype, etc. See clinical info

     $short_sample_type = $sample_name_list;

     $alt_filename = join(".", $sample_name_list, lc( $experimental_strategy ), "bam" );


 if( $bHead == 1) {
     print join("\t", qw / project_id      case_id     aliquot_id_list   sample_name_list    sample_type_list   sample_type_group       preservation_method_list        data_category   data_type       caller  call_format     experimental_strategy   md5     size    parent_dir  gdc_filename    alt_filename    reference  disease  alt_sample_name  gdc_file_id  system  /),"\n";

     $bHead = 0;
  }
   print join("\t", $project_id, $submitter_id,  $aliquot_id_list,  $sample_name_list, $sample_type_list,  $sample_type_group,  $preservation_method_list, $data_category, $data_type, $caller, $call_format, $experimental_strategy, $md5,  $size, $parent_dir, $gdc_filename, $alt_filename,  $ENV{REFERENCE_SHORT}, $disease, $alt_sample_name, $gdc_file_id, $cluster   ),"\n";

}
}
close(IN);
'

