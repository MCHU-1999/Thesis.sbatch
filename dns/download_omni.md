```bash
apptainer exec \
        --containall \
        -B /tudelft.net/:/tudelft.net/ \
        --pwd /tudelft.net/staff-umbrella/Deep3D/mingchiehhu/dn-splatter \
        /tudelft.net/staff-umbrella/Deep3D/mingchiehhu/containers/dnsplatter.sif \
        python dn_splatter/data/download_scripts/download_omnidata.py
```
