FROM centos:7.8.2003

ENV GO111MODULE on
#ENV GOPROXY=http://192.168.82.28:3000
ENV TF_LOG DEBUG 
ENV TF_LOG_PATH /tmp/tf_caep.log

#RUN apk add bash git wget util-linux pkgconfig libvirt-dev build-base qemu-img qemu-system-x86_64 bash curl
RUN yum install -y make gcc vim git wget unzip

WORKDIR /root/terraform-provider-caep
RUN wget https://releases.hashicorp.com/terraform/1.0.5/terraform_1.0.5_linux_amd64.zip && \
        unzip ./terraform_1.0.5_linux_amd64.zip -d /usr/local/bin && rm -f terraform_1.0.5_linux_amd64.zip

RUN wget https://dl.google.com/go/go1.17.2.linux-amd64.tar.gz && \
    tar xzf ./go1.17.2.linux-amd64.tar.gz -C /usr/local &&    \
    printf "export PATH=\$PATH:/usr/local/go/bin\n" >> /root/.bashrc &&  \
    rm -f go1.17.2.linux-amd64.tar.gz

COPY ./ ./

RUN source /root/.bashrc && \
    cd /root/terraform-provider-caep && \
    make install

RUN yum -y install openssh-server openssh-clients initscripts

RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N ''
RUN ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key -N ''
RUN ssh-keygen -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -N ''
RUN ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N ''

#RUN sed -i "s/#UsePrivilegeSeparation.*/UsePrivilegeSeparation no/g" /etc/ssh/sshd_config
#RUN sed -i "s/UsePAM.*/UsePAM no/g" /etc/ssh/sshd_config
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

RUN useradd -ms /bin/bash caeper &&   \
    mkdir -p /home/caeper/.ssh    &&  \
    ssh-keygen -t ecdsa -N '' -f /home/caeper/.ssh/caeper_id_ecdsa  &&  \
    cp /home/caeper/.ssh/caeper_id_ecdsa.pub /home/caeper/.ssh/authorized_keys   &&  \
    chown caeper.caeper -R /home/caeper   &&  \
    chmod 0400  /home/caeper/.ssh/caeper_id_ecdsa

RUN echo 'caeper:pass123' | chpasswd
RUN cp -aR /root/.terraform.d /home/caeper
COPY ./examples /home/caeper
COPY ./caeper.vimrc /home/caeper/.vimrc

RUN mkdir -p /home/caeper/.vim/autoload  /home/caeper/.vim/bundle && \
curl -LSso /home/caeper/.vim/autoload/pathogen.vim https://tpo.pe/pathogen.vim

RUN git clone https://github.com/hashivim/vim-terraform.git /home/caeper/.vim/bundle/vim-terraform    \
    && chown caeper.caeper -R /home/caeper 

EXPOSE 22
EXPOSE 10287


RUN yum install -y git unzip nmap wget python3 pip3
RUN pip3 install --user pytest

#ADD ./pytester.tgz / 
RUN mv ./pytester /
RUN pip3 install --user -r /pytester/pytest.req.txt
RUN chmod +x /root/terraform-provider-caep/entrypoint.sh

#CMD ["/tf_caep_provider_bin","--listen-port=12345","--log-level=debug"]
#CMD ["/usr/sbin/init"]
#CMD ["/usr/sbin/sshd","-D"]
CMD ["bash","-c","/root/terraform-provider-caep/entrypoint.sh"]

